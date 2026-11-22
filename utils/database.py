"""Database helpers: one MySQL connection per request using PyMySQL.

All SQL in EcoQuest is parameterized (%s placeholders) to prevent SQL injection.
"""
import pymysql
import pymysql.cursors
from flask import g

import config


def connect(database=None):
    """Open a new MySQL connection (autocommit off: we commit explicitly)."""
    return pymysql.connect(
        host=config.DB_HOST,
        port=config.DB_PORT,
        user=config.DB_USER,
        password=config.DB_PASSWORD,
        database=database or config.DB_NAME,
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=False,
    )


def get_db():
    """Return the connection for the current request (created on first use)."""
    if "db" not in g:
        g.db = connect()
    return g.db


def close_db(error=None):
    db = g.pop("db", None)
    if db is not None:
        if error is not None:
            db.rollback()
        db.close()


# ---- small helpers that work on any connection ------------------------------
def fetch_all(conn, sql, args=None):
    with conn.cursor() as cur:
        cur.execute(sql, args or ())
        return cur.fetchall()


def fetch_one(conn, sql, args=None):
    with conn.cursor() as cur:
        cur.execute(sql, args or ())
        return cur.fetchone()


def execute(conn, sql, args=None):
    """Run INSERT/UPDATE/DELETE. Returns the last inserted id."""
    with conn.cursor() as cur:
        cur.execute(sql, args or ())
        return cur.lastrowid
