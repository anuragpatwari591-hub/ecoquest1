# System Architecture

EcoQuest uses a simple **three-tier architecture**.

```mermaid
flowchart TD
    B["User Browser<br/>HTML / CSS / JavaScript (+ Chart.js)"] -->|HTTP request| F["Flask application (app.py)"]
    F --> R["Routes (Blueprints)<br/>auth, student, quiz, challenge, teacher, admin"]
    R --> U["Business logic (utils/)<br/>auth.py, gamification.py"]
    R --> D["Data access helpers (utils/database.py)"]
    U --> D
    D -->|PyMySQL, parameterized SQL| M[("MySQL database")]
    R -->|render_template| T["Jinja2 templates"]
    T -->|HTML response| B
```

| Layer | Technology | Where in the project |
|---|---|---|
| Presentation | HTML5, CSS3, vanilla JavaScript, Chart.js | `templates/`, `static/` |
| Application | Python, Flask | `app.py`, `routes/`, `utils/` |
| Data | MySQL (PyMySQL driver) | `database/schema.sql`, `utils/database.py` |

## Request flow (example: completing a lesson)

1. The browser sends `POST /student/lessons/1/complete` with the session cookie and CSRF token.
2. `check_csrf` (before-request hook) validates the token; `@login_required("student")` checks the session role.
3. The route inserts a row into `user_progress`, then calls `record_activity()` in `utils/gamification.py`.
4. `record_activity()` adds XP, writes `activity_log`, updates the streak and awards any newly satisfied badges.
5. The route commits the transaction and redirects with flash messages (XP and badge notifications).

## Component diagram

```mermaid
flowchart TB
    subgraph Browser
      Pages["Jinja2-rendered pages"]
      JS["main.js (quiz navigation, charts)"]
    end
    subgraph Flask["Flask application"]
      APP["app.py (create_app, CSRF, error pages)"]
      AUTHR["routes/auth.py"]
      STUR["routes/student.py"]
      QUIZR["routes/quiz.py"]
      CHR["routes/challenge.py"]
      TEAR["routes/teacher.py"]
      ADMR["routes/admin.py"]
      UAUTH["utils/auth.py"]
      UGAME["utils/gamification.py"]
      UDB["utils/database.py"]
      CFG["config.py (.env)"]
    end
    DB[("MySQL")]
    Pages --> APP
    APP --> AUTHR & STUR & QUIZR & CHR & TEAR & ADMR
    AUTHR --> UAUTH
    STUR & QUIZR & CHR --> UGAME
    AUTHR & STUR & QUIZR & CHR & TEAR & ADMR & UGAME --> UDB
    UDB --> DB
    UDB --> CFG
```

## Deployment diagram

Local development (verified) and the intended cloud layout (prepared, **not deployed or verified**):

```mermaid
flowchart LR
    subgraph Local["Local development (verified)"]
      L1["Browser"] --> L2["python app.py<br/>Flask dev server :5000"] --> L3[("MySQL localhost:3306")]
    end
    subgraph Cloud["Cloud (prepared, not deployed)"]
      C1["Browser"] --> C2["Railway service<br/>gunicorn app:app"] --> C3[("Railway MySQL")]
      G["GitHub repository"] -.->|deploy| C2
    end
```

## Roles and access control

| Role | Can open | Enforced by |
|---|---|---|
| Student | `/student/*`, `/quiz/*`, `/challenges/*` | `@login_required("student")` |
| Teacher | `/teacher/*`, leaderboard, profile | `@login_required("teacher")` |
| Admin | `/admin/*` and also all `/teacher/*` pages | `@login_required("admin")`; admin passes teacher checks |

The decorator in `utils/auth.py` reads `session["role"]` (set at login from the database) and redirects unauthorised users.

## Security measures actually implemented

* Passwords hashed with Werkzeug (`generate_password_hash`).
* Server-side sessions via a signed cookie (`HttpOnly`, `SameSite=Lax`; `Secure` configurable by env var).
* Role-based authorisation on every protected route.
* Parameterised SQL everywhere (`%s` placeholders) — no string-formatted user input in queries.
* CSRF token on every POST form.
* Jinja2 auto-escaping of all output (prevents XSS from user-entered text).
* Quiz answers are graded on the server; correct answers are never sent to the browser while taking a quiz.
* Secrets and DB credentials come from environment variables (`.env`, not committed).

These are practical project-level protections; the application has not had an independent security audit.
