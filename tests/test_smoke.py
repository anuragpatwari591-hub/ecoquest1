"""Smoke test: every main page renders (HTTP 200) for the right role (TC-47 .. TC-49)."""
STUDENT_PAGES = ["/", "/student/dashboard", "/student/topics", "/student/topics/1", "/student/lessons/1",
                 "/quiz/", "/quiz/1", "/quiz/1/take", "/quiz/history", "/challenges/",
                 "/student/leaderboard", "/student/leaderboard?class_name=Class 10-A", "/student/progress", "/student/profile"]
TEACHER_PAGES = ["/teacher/dashboard", "/teacher/students", "/teacher/students/3", "/teacher/quizzes",
                 "/teacher/quizzes/1/questions", "/teacher/challenges", "/student/profile"]
ADMIN_PAGES = ["/admin/dashboard", "/admin/users", "/admin/users?role=student", "/admin/topics", "/admin/lessons",
               "/admin/lessons/new", "/admin/lessons/1/edit", "/admin/badges"] + TEACHER_PAGES


def _check(client, pages):
    for url in pages:
        r = client.get(url)
        assert r.status_code == 200, f"{url} -> {r.status_code}"


def test_student_pages_render(student):      # TC-47
    _check(student, STUDENT_PAGES)


def test_teacher_pages_render(teacher):      # TC-48
    _check(teacher, TEACHER_PAGES)


def test_admin_pages_render(admin):          # TC-49
    _check(admin, ADMIN_PAGES)


def test_unknown_page_shows_404(client):     # TC-50
    r = client.get("/no-such-page")
    assert r.status_code == 404 and b"does not exist" in r.data
