"""EcoQuest as a Windows desktop application.

Opens EcoQuest in its own window (Microsoft Edge WebView2, no browser or address bar).
Behind the scenes it starts the MySQL database (if needed) and the app server on a free
port, and shuts down what it started when the window is closed.

Run from source:  python desktop_app.py       Build the .exe:  build_exe.ps1
"""
import ctypes
import logging
import os
import socket
import subprocess
import sys
import threading
import time

FROZEN = getattr(sys, "frozen", False)
BASE = os.path.dirname(sys.executable) if FROZEN else os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE)

# ---- settings: .env next to the program (database login, secret key) -------------------
from dotenv import load_dotenv  # noqa: E402

load_dotenv(os.path.join(BASE, ".env"))
MYSQL_BIN = os.environ.get("MYSQL_BIN", r"C:\Program Files\MySQL\MySQL Server 8.4\bin")
MYSQL_DATADIR = os.environ.get("MYSQL_DATADIR", os.path.join(os.path.expanduser("~"), "ecoquest-mysql-data"))

os.makedirs(os.path.join(BASE, "logs"), exist_ok=True)
logging.basicConfig(filename=os.path.join(BASE, "logs", "desktop.log"), level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("ecoquest")

NO_WINDOW = 0x08000000  # CREATE_NO_WINDOW


def message(text, title="EcoQuest", error=True):
    ctypes.windll.user32.MessageBoxW(0, text, title, 0x10 if error else 0x40)


def port_open(port, host="127.0.0.1"):
    with socket.socket() as s:
        s.settimeout(0.4)
        return s.connect_ex((host, port)) == 0


def free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


class Backend:
    def __init__(self):
        self.started_mysql = False
        self.port = free_port()

    def start_mysql(self):
        db_port = int(os.environ.get("DB_PORT", "3306"))
        if port_open(db_port):
            return
        mysqld = os.path.join(MYSQL_BIN, "mysqld.exe")
        if not os.path.exists(mysqld):
            raise RuntimeError(f"MySQL was not found at:\n{MYSQL_BIN}\n\nInstall MySQL 8.4 or set MYSQL_BIN in the .env file.")
        log.info("starting MySQL")
        subprocess.Popen([mysqld, f"--datadir={MYSQL_DATADIR}", "--bind-address=127.0.0.1", f"--port={db_port}"],
                         creationflags=NO_WINDOW)
        self.started_mysql = True
        for _ in range(90):
            if port_open(db_port):
                return
            time.sleep(1)
        raise RuntimeError("The MySQL database did not start in time.")

    def start_server(self):
        import init_db
        init_db.init()                                  # creates tables / content only if missing
        from waitress import serve
        from app import app
        threading.Thread(target=lambda: serve(app, host="127.0.0.1", port=self.port, threads=8), daemon=True).start()
        for _ in range(60):
            if port_open(self.port):
                return
            time.sleep(0.5)
        raise RuntimeError("The EcoQuest server did not start.")

    def stop(self):
        if self.started_mysql:
            try:
                subprocess.run([os.path.join(MYSQL_BIN, "mysqladmin.exe"), "-uroot", "shutdown"],
                               creationflags=NO_WINDOW, timeout=30)
            except Exception:
                log.exception("could not stop MySQL cleanly")


LOADING = """<html><body style="margin:0;display:grid;place-items:center;height:100vh;background:#f6faf5;
font-family:Segoe UI,Arial,sans-serif;color:#14532d"><div style="text-align:center">
<div style="font-size:64px">&#127793;</div><h1 style="margin:.2em 0">EcoQuest</h1>
<p style="color:#6b7280">Learn. Play. Act. Make an Impact.</p><p>Starting up&hellip;</p></div></body></html>"""


def main():
    # only one EcoQuest window at a time
    mutex = ctypes.windll.kernel32.CreateMutexW(None, False, "EcoQuestDesktopApp")
    if ctypes.windll.kernel32.GetLastError() == 183:  # ERROR_ALREADY_EXISTS
        message("EcoQuest is already running.", error=False)
        return
    import webview

    backend = Backend()
    window = webview.create_window("EcoQuest", html=LOADING, width=1280, height=820, min_size=(900, 600))

    def boot():
        try:
            backend.start_mysql()
            backend.start_server()
            window.load_url(f"http://127.0.0.1:{backend.port}/")
        except Exception as exc:
            log.exception("startup failed")
            message(f"EcoQuest could not start.\n\n{exc}\n\nDetails: {os.path.join(BASE, 'logs', 'desktop.log')}")
            window.destroy()

    webview.start(boot, gui="edgechromium")
    backend.stop()
    os._exit(0)


if __name__ == "__main__":
    main()
