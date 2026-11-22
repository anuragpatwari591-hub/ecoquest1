# Deployment Documentation

## Status
* **Local deployment:** verified (Windows 11, Python 3.11, MySQL 8.4, Flask development server).
* **Cloud deployment (Railway):** **prepared but NOT deployed or verified.** No public URL exists. Deployment needs the
  student's own GitHub and Railway accounts (manual authorisation).

## Local setup
```powershell
# 1. Install Python 3.11+ and MySQL 8
python -m venv venv ; .\venv\Scripts\Activate.ps1
pip install -r requirements.txt
# 2. Create a MySQL user/database (as MySQL root)
#    CREATE DATABASE ecoquest CHARACTER SET utf8mb4;
#    CREATE USER 'ecoquest'@'localhost' IDENTIFIED BY 'choose-a-password';
#    GRANT ALL ON ecoquest.* TO 'ecoquest'@'localhost';
# 3. Configure
copy .env.example .env      # then edit the values
# 4. Create tables and demo data
python init_db.py
python create_admin.py       # create your own admin account
# 5. Run
python app.py               # http://127.0.0.1:5000
```

## Environment variables
| Variable | Purpose |
|---|---|
| `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME` | MySQL connection (Railway's `MYSQLHOST`, `MYSQLPORT`, `MYSQLUSER`, `MYSQLPASSWORD`, `MYSQLDATABASE` are also read) |
| `SECRET_KEY` | Signs session cookies. **Required in production**; if missing a random key is generated per start (sessions reset on restart) |
| `FLASK_DEBUG` | `1` only for local development |
| `SESSION_COOKIE_SECURE` | Set `1` when served over HTTPS |
| `PORT` | Port provided by the host |

## Railway deployment steps (prepared)
1. Push the repository to GitHub.
2. In Railway: **New Project → Deploy from GitHub repo**.
3. Add a **MySQL** database to the project; reference its variables in the web service (`MYSQLHOST`… are read automatically).
4. Set `SECRET_KEY` (a long random string) and `SESSION_COOKIE_SECURE=1` in the web service variables.
5. The included `Procfile` starts the app: `web: gunicorn app:app --bind 0.0.0.0:$PORT`.
6. Once the service and database are up, run `python init_db.py` once and then `python create_admin.py` (Railway shell/one-off command) to create tables, study content and your admin account.
7. Open the generated public domain and verify login with the demo accounts, then **change or remove the demo passwords** for any public deployment.

## Production notes
* Never use the Flask development server in production (use gunicorn as in the `Procfile`).
* Demo account passwords are documented publicly in the README — change them before real use.
* Charts load Chart.js from cdnjs; the page works without it but charts will be blank.
