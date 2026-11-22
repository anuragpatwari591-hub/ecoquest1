"""Run EcoQuest with the Waitress production server (works on Windows, no debug mode).

Used by start_ecoquest.ps1. Log file: logs/server.log
"""
import logging
import os

from waitress import serve

import config
from app import app

LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
os.makedirs(LOG_DIR, exist_ok=True)
logging.basicConfig(filename=os.path.join(LOG_DIR, "server.log"), level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(message)s")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    logging.info("EcoQuest starting on http://127.0.0.1:%s", port)
    serve(app, host="127.0.0.1", port=port, threads=8)
