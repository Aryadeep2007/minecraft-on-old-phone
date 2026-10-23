"""Loopback-only control panel for a Paper server managed by Termux."""

from __future__ import annotations

import hmac
import os
import re
import subprocess
import tarfile
import time
from datetime import datetime, timezone
from functools import wraps
from pathlib import Path
from threading import Lock

from flask import Flask, abort, flash, redirect, render_template, request, session, url_for

from dashboard.rcon import RconClient, RconError


ROOT = Path(__file__).resolve().parents[1]
SERVER_DIR = Path(os.environ.get("MINECRAFT_SERVER_DIR", str(Path.home() / "minecraft-server"))).expanduser()
BACKUP_DIR = Path(os.environ.get("BACKUP_DIR", str(SERVER_DIR / "backups"))).expanduser()
PLAYER_NAME = re.compile(r"^[A-Za-z0-9_]{3,16}$")
LOGIN_LIMIT = 5
LOCKOUT_SECONDS = 300
_login_attempts: dict[str, tuple[int, float]] = {}
_login_lock = Lock()


def create_app() -> Flask:
    required = ("FLASK_SECRET_KEY", "DASHBOARD_PASSWORD", "RCON_PASSWORD")
    missing = [name for name in required if not os.environ.get(name)]
    if missing:
        raise RuntimeError("Missing required environment variables: " + ", ".join(missing))
    rcon_host = os.environ.get("RCON_HOST", "127.0.0.1")
    if rcon_host not in {"127.0.0.1", "localhost", "::1"}:
        raise RuntimeError("RCON_HOST must refer to loopback; remote RCON is not supported")
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config.update(
        SECRET_KEY=os.environ["FLASK_SECRET_KEY"],
        DASHBOARD_PASSWORD=os.environ.get("DASHBOARD_PASSWORD", ""),
        RCON_HOST=rcon_host,
        RCON_PORT=int(os.environ.get("RCON_PORT", "25575")),
        RCON_PASSWORD=os.environ.get("RCON_PASSWORD", ""),
        PERMANENT_SESSION_LIFETIME=8 * 60 * 60,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SECURE=False,  # HTTP is carried only inside the encrypted SSH local forward.
        SESSION_COOKIE_SAMESITE="Strict",
        MAX_CONTENT_LENGTH=8 * 1024,
        TRUSTED_HOSTS=["127.0.0.1", "localhost"],
    )

    @app.after_request
    def add_security_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; style-src 'self'; form-action 'self'; "
            "frame-ancestors 'none'; base-uri 'self'"
        )
        response.headers["Cache-Control"] = "no-store"
        return response

    def require_login(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            if not session.get("authenticated"):
                return redirect(url_for("login"))
            return view(*args, **kwargs)

        return wrapped

    def csrf_token() -> str:
        token = session.get("csrf_token")
        if not token:
            import secrets

            token = secrets.token_urlsafe(32)
            session["csrf_token"] = token
        return token

    app.jinja_env.globals["csrf_token"] = csrf_token

    @app.before_request
    def protect_mutations():
        if request.method == "POST" and request.endpoint != "login":
            if not session.get("authenticated"):
                return redirect(url_for("login"))
            sent = request.form.get("csrf_token", "")
            saved = session.get("csrf_token", "")
            if not sent or not saved or not hmac.compare_digest(sent, saved):
                abort(400, "Invalid request token")

    def rcon() -> RconClient:
        return RconClient(
            app.config["RCON_HOST"],
            app.config["RCON_PORT"],
            app.config["RCON_PASSWORD"],
        )

    def server_process_running() -> bool:
        proc_root = Path("/proc")
        try:
            entries = proc_root.iterdir()
        except OSError:
            return False
        for entry in entries:
            if not entry.name.isdigit():
                continue
            try:
                args = (entry / "cmdline").read_bytes().replace(b"\0", b" ")
            except OSError:
                continue
            if b"java" in args and b"-jar" in args and b"paper.jar" in args:
                return True
        return False

    def start_server() -> None:
        start_script = SERVER_DIR / "start.sh"
        if not start_script.is_file():
            raise RuntimeError("Paper start script was not found")
        if server_process_running():
            raise RuntimeError("Paper is already running")
        log_dir = SERVER_DIR / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        with (log_dir / "console.log").open("ab") as log_file:
            subprocess.Popen(
                ["/data/data/com.termux/files/usr/bin/sh", str(start_script)],
                cwd=SERVER_DIR,
                stdin=subprocess.DEVNULL,
                stdout=log_file,
                stderr=subprocess.STDOUT,
                close_fds=True,
                start_new_session=True,
            )

    def create_backup() -> str:
        backup_roots = [SERVER_DIR / name for name in ("world", "world_nether", "world_the_end")]
        existing = [path for path in backup_roots if path.is_dir()]
        if not existing:
            raise RuntimeError("No world folders were found")

        backup_dir = BACKUP_DIR.resolve()
        if backup_dir == SERVER_DIR.resolve() or SERVER_DIR.resolve() in backup_dir.parents:
            raise RuntimeError("Backup directory must be outside the server folder")
        backup_dir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        target = backup_dir / f"world-{stamp}.tar.gz"

        rcon().run("save-off")
        try:
            rcon().run("save-all flush")
            with tarfile.open(target, mode="w:gz") as archive:
                for folder in existing:
                    archive.add(folder, arcname=folder.name, recursive=True)
        except Exception:
            target.unlink(missing_ok=True)
            raise
        finally:
            try:
                rcon().run("save-on")
            except RconError:
                app.logger.exception("Could not re-enable world saving after backup")
        return target.name

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if session.get("authenticated"):
            return redirect(url_for("index"))
        if request.method == "POST":
            client = request.remote_addr or "unknown"
            now = time.monotonic()
            with _login_lock:
                failures, lockout_until = _login_attempts.get(client, (0, 0.0))
                if lockout_until > now:
                    abort(429, "Too many login attempts; wait before trying again")

            expected = app.config["DASHBOARD_PASSWORD"]
            provided = request.form.get("password", "")
            if hmac.compare_digest(provided, expected):
                with _login_lock:
                    _login_attempts.pop(client, None)
                session.clear()
                session["authenticated"] = True
                session.permanent = True
                return redirect(url_for("index"))

            with _login_lock:
                failures += 1
                if failures >= LOGIN_LIMIT:
                    _login_attempts[client] = (0, now + LOCKOUT_SECONDS)
                else:
                    _login_attempts[client] = (failures, 0.0)
            flash("Login failed.", "error")
        return render_template("login.html")

    @app.post("/logout")
    @require_login
    def logout():
        session.clear()
        return redirect(url_for("login"))

    @app.get("/")
    @require_login
    def index():
        status = "Running" if server_process_running() else "Stopped"
        players = "RCON unavailable"
        try:
            players = rcon().run("list")
        except RconError:
            pass
        backups = []
        if BACKUP_DIR.is_dir():
            backups = sorted(
                (item for item in BACKUP_DIR.glob("world-*.tar.gz") if item.is_file()),
                key=lambda item: item.stat().st_mtime,
                reverse=True,
            )[:10]
        return render_template("dashboard.html", status=status, players=players, backups=backups)

    @app.post("/console")
    @require_login
    def console():
        command = request.form.get("command", "").strip()
        try:
            output = rcon().run(command)
            flash(output or "Command sent.", "success")
        except RconError as exc:
            flash(str(exc), "error")
        return redirect(url_for("index"))

    @app.post("/server/<action>")
    @require_login
    def server_action(action: str):
        try:
            if action == "start":
                start_server()
                flash("Paper start requested.", "success")
            elif action == "stop":
                rcon().run("stop")
                flash("Paper stop requested.", "success")
            elif action == "restart":
                rcon().run("stop")
                deadline = time.monotonic() + 120
                while server_process_running() and time.monotonic() < deadline:
                    time.sleep(1)
                if server_process_running():
                    raise RuntimeError("Paper did not stop within 120 seconds")
                start_server()
                flash("Paper restart requested.", "success")
            else:
                abort(404)
        except (RconError, RuntimeError, OSError) as exc:
            flash(str(exc), "error")
        return redirect(url_for("index"))

    @app.post("/whitelist/<action>")
    @require_login
    def whitelist(action: str):
        name = request.form.get("name", "").strip()
        if not PLAYER_NAME.fullmatch(name):
            flash("Enter a Java username using 3–16 letters, numbers, or underscores.", "error")
            return redirect(url_for("index"))
        if action not in {"add", "remove"}:
            abort(404)
        try:
            output = rcon().run(f"whitelist {action} {name}")
            flash(output or f"Whitelist {action} requested for {name}.", "success")
        except RconError as exc:
            flash(str(exc), "error")
        return redirect(url_for("index"))

    @app.post("/backup")
    @require_login
    def backup():
        try:
            name = create_backup()
            flash(f"World backup created: {name}", "success")
        except (RconError, RuntimeError, OSError, tarfile.TarError) as exc:
            flash(str(exc), "error")
        return redirect(url_for("index"))

    return app


app = create_app()
