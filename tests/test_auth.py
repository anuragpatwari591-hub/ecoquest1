"""Authentication and authorization tests (TC-01 .. TC-10)."""
from conftest import login, one


def test_register_student_success(client, db):                           # TC-01
    r = client.post("/register", data={"name": "New Kid", "email": "newkid@example.com", "password": "secret1"})
    assert r.status_code == 302 and "/student/dashboard" in r.location      # auto-logged-in
    row = one(db, "SELECT u.password_hash, r.role_name FROM users u JOIN roles r ON u.role_id=r.role_id "
                  "WHERE email='newkid@example.com'")
    assert row["role_name"] == "student"
    assert row["password_hash"] != "secret1"          # never plaintext
    assert row["password_hash"].startswith(("scrypt:", "pbkdf2:"))


def test_register_duplicate_email_rejected(client):                      # TC-02
    r = client.post("/register", data={"name": "Dup", "email": "student@ecoquest.test", "password": "secret1"})
    assert r.status_code == 400
    assert b"already exists" in r.data


def test_register_validation_errors(client):                             # TC-03
    r = client.post("/register", data={"name": "A", "email": "bad-email", "password": "123"})
    assert r.status_code == 400
    assert b"valid email" in r.data and b"at least 6" in r.data


def test_login_valid_student_redirects_to_dashboard(client):             # TC-04
    r = login(client, "student")
    assert r.status_code == 302 and "/student/dashboard" in r.location


def test_login_invalid_password(client):                                 # TC-05
    r = client.post("/login", data={"email": "student@ecoquest.test", "password": "wrong"})
    assert r.status_code == 401 and b"Invalid email or password" in r.data


def test_logout_clears_session(client):                                  # TC-06
    login(client, "student")
    client.get("/logout")
    r = client.get("/student/dashboard")
    assert r.status_code == 302 and "/login" in r.location


def test_anonymous_redirected_to_login(client):                          # TC-07
    for url in ("/student/dashboard", "/teacher/dashboard", "/admin/dashboard", "/quiz/"):
        r = client.get(url)
        assert r.status_code == 302 and "/login" in r.location


def test_student_blocked_from_teacher_and_admin(student):                # TC-08
    for url in ("/teacher/dashboard", "/teacher/quizzes", "/admin/dashboard", "/admin/users"):
        r = student.get(url)
        assert r.status_code == 302 and "/student/dashboard" in r.location


def test_teacher_blocked_from_admin_but_not_teacher_pages(teacher):      # TC-09
    assert teacher.get("/admin/dashboard").status_code == 302
    assert teacher.get("/admin/users").status_code == 302
    assert teacher.get("/teacher/dashboard").status_code == 200
    assert teacher.get("/student/dashboard").status_code == 302          # teachers have no student dashboard


def test_admin_can_access_admin_and_teacher_pages(admin):                # TC-10
    for url in ("/admin/dashboard", "/admin/users", "/admin/topics", "/admin/lessons",
                "/admin/badges", "/teacher/dashboard", "/teacher/quizzes"):
        assert admin.get(url).status_code == 200


def test_disabled_user_cannot_login(client, db):                         # TC-11
    with db.cursor() as cur:
        cur.execute("UPDATE users SET is_active = 0 WHERE email = 'student@ecoquest.test'")
    db.commit()
    r = login(client, "student")
    assert r.status_code == 401


def test_csrf_blocks_post_without_token(app):                            # TC-12
    app.config["CSRF_ENABLED"] = True
    c = app.test_client()
    r = c.post("/login", data={"email": "student@ecoquest.test", "password": "Student@123"})
    assert r.status_code == 400
