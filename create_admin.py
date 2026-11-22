"""Create a real administrator or teacher account (no demo passwords).

Usage:
    python create_admin.py                       # asks for name, email and password
    python create_admin.py --role teacher        # create a teacher instead
"""
import getpass
import sys

import pymysql

from utils.auth import hash_password, validate_registration
from utils.database import connect, execute, fetch_one


def main():
    role = "teacher" if "--role" in sys.argv and sys.argv[sys.argv.index("--role") + 1] == "teacher" else "admin"
    name = input("Full name: ").strip()
    email = input("Email: ").strip().lower()
    password = getpass.getpass("Password (min 6 characters): ")
    if password != getpass.getpass("Repeat password: "):
        sys.exit("Passwords do not match.")
    errors = validate_registration(name, email, password)
    if errors:
        sys.exit("\n".join(errors))
    conn = connect()
    try:
        role_id = fetch_one(conn, "SELECT role_id FROM roles WHERE role_name = %s", (role,))["role_id"]
        execute(conn, "INSERT INTO users (name, email, password_hash, role_id) VALUES (%s,%s,%s,%s)",
                (name, email, hash_password(password), role_id))
        conn.commit()
        print(f"{role.title()} account created for {email}. You can now log in.")
    except pymysql.IntegrityError:
        sys.exit("An account with that email already exists.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
