# Testing Documentation

All tests are automated with **pytest** and run against a separate MySQL database `ecoquest_test`
(the schema and demo content are re-created at the start of each run; user-generated rows are cleared before every test).

Run: `python -m pytest -v`

Last executed: **2026-11-22** — pytest summary line: `68 passed in 19.82s`

Test case mapping: each `TC-xx` below is the comment on the corresponding test function in `tests/`.
Parameterised tests count as one test case here. Total documented test cases: **60** — passed: **60**.

| Test Case ID | Description | Precondition | Steps | Expected Result | Actual Result | Status |
|---|---|---|---|---|---|---|
| TC-01 | Register a new student | Fresh seeded test database (ecoquest_test) | POST /register with valid name, email, password | Account created as student; password stored hashed (not plaintext) | As expected | Passed |
| TC-02 | Register with an existing email | Fresh seeded test database (ecoquest_test) | POST /register using student@ecoquest.test | HTTP 400 and 'already exists' message | As expected | Passed |
| TC-03 | Register with invalid data | Fresh seeded test database (ecoquest_test) | POST /register with 1-char name, bad email, 3-char password | HTTP 400 with validation messages | As expected | Passed |
| TC-04 | Valid student login | Fresh seeded test database (ecoquest_test) | POST /login with demo student credentials | Redirect to /student/dashboard | As expected | Passed |
| TC-05 | Login with wrong password | Fresh seeded test database (ecoquest_test) | POST /login with wrong password | HTTP 401 and 'Invalid email or password' | As expected | Passed |
| TC-06 | Logout | Fresh seeded test database (ecoquest_test) | Login, GET /logout, then GET /student/dashboard | Redirected to /login (session cleared) | As expected | Passed |
| TC-07 | Anonymous access to protected pages | Fresh seeded test database (ecoquest_test) | GET dashboards and /quiz/ without login | Redirect to /login | As expected | Passed |
| TC-08 | Student blocked from teacher/admin | Fresh seeded test database (ecoquest_test) | Login as student; GET teacher and admin URLs | Redirect to student dashboard (no access) | As expected | Passed |
| TC-09 | Teacher blocked from admin | Fresh seeded test database (ecoquest_test) | Login as teacher; GET admin URLs and teacher dashboard | Admin URLs redirected; teacher dashboard 200 | As expected | Passed |
| TC-10 | Admin access | Fresh seeded test database (ecoquest_test) | Login as admin; GET admin and teacher URLs | All return HTTP 200 | As expected | Passed |
| TC-11 | Disabled account login | Fresh seeded test database (ecoquest_test) | Set is_active=0; attempt login | Login refused (HTTP 401) | As expected | Passed |
| TC-12 | CSRF protection | Fresh seeded test database (ecoquest_test) | Enable CSRF; POST /login without token | HTTP 400 | As expected | Passed |
| TC-13 | Quiz pages load; answers not exposed | Fresh seeded test database (ecoquest_test) | GET /quiz/ and /quiz/1/take as student | HTTP 200; page does not contain is_correct | As expected | Passed |
| TC-14 | Perfect quiz | Fresh seeded test database (ecoquest_test) | Submit all-correct answers for quiz 3 (5 questions) | Score 5/5; XP = 5x10 + 50 = 100 | As expected | Passed |
| TC-15 | Partial quiz score | Fresh seeded test database (ecoquest_test) | Submit 3 correct of 5 | Score 3; XP 30; no bonus | As expected | Passed |
| TC-16 | All wrong answers | Fresh seeded test database (ecoquest_test) | Submit all wrong answers | Score 0; XP 0 | As expected | Passed |
| TC-17 | Attempt persisted in DB | Fresh seeded test database (ecoquest_test) | Submit quiz; query quiz_attempts, quiz_answers, users | 1 attempt, 5 answers stored, user XP updated | As expected | Passed |
| TC-18 | Result page and review | Fresh seeded test database (ecoquest_test) | Submit quiz and follow redirect | Page shows 'Quiz Complete', score 4/5, answer review | As expected | Passed |
| TC-19 | Tampered answer | Fresh seeded test database (ecoquest_test) | Submit an option id belonging to another question | Counted as unanswered; score 0 | As expected | Passed |
| TC-20 | Result privacy | Fresh seeded test database (ecoquest_test) | Another student requests someone else's attempt | HTTP 404 | As expected | Passed |
| TC-21 | Level formula | Fresh seeded test database (ecoquest_test) | calculate_level for 0, 99, 100, 199, 250, 1000 XP | Levels 1,1,2,2,3,11 | As expected | Passed |
| TC-22 | Level progress info | Fresh seeded test database (ecoquest_test) | level_info(250) | Level 3, 50 XP into level, 50 to next, 50% | As expected | Passed |
| TC-23 | Quiz XP formula | Fresh seeded test database (ecoquest_test) | calculate_quiz_xp for (8/10),(10/10),(0/10),(5/5) | 80, 150, 0, 100 | As expected | Passed |
| TC-24 | Streak rule | Fresh seeded test database (ecoquest_test) | next_streak for first, same day, consecutive, missed day | 1, unchanged, +1, reset to 1 | As expected | Passed |
| TC-25 | 7-day streak bonus | Fresh seeded test database (ecoquest_test) | Streak 6 active yesterday; update_streak today | Streak 7; +100 XP | As expected | Passed |
| TC-26 | Complete lesson | Fresh seeded test database (ecoquest_test) | POST /student/lessons/1/complete | +10 XP; progress row; Green Beginner badge | As expected | Passed |
| TC-27 | Duplicate lesson completion | Fresh seeded test database (ecoquest_test) | Complete same lesson twice | XP awarded only once (10) | As expected | Passed |
| TC-28 | Eco Champion badge | Fresh seeded test database (ecoquest_test) | Set XP 1000; check_badges twice | Badge awarded once | As expected | Passed |
| TC-29 | Eco Learner badge | Fresh seeded test database (ecoquest_test) | Insert 5 attempts; check_badges | Eco Learner awarded | As expected | Passed |
| TC-30 | Leaderboard order | Fresh seeded test database (ecoquest_test) | Set XP for 3 students; call leaderboard and student_rank | Sorted by XP desc; ranks correct; students only | As expected | Passed |
| TC-31 | Leaderboard class filter | Fresh seeded test database (ecoquest_test) | leaderboard(class_name='Class 10-B') | Only students of that class | As expected | Passed |
| TC-32 | Topic progress | Fresh seeded test database (ecoquest_test) | Compare progress before/after completing a lesson | 0% before, >0% after | As expected | Passed |
| TC-33 | Complete challenge | Fresh seeded test database (ecoquest_test) | POST /challenges/1/complete | +20 XP; completion row stored | As expected | Passed |
| TC-34 | Duplicate challenge same day | Fresh seeded test database (ecoquest_test) | Complete challenge 1 twice | Second attempt refused; XP not doubled | As expected | Passed |
| TC-35 | DB uniqueness constraint | Fresh seeded test database (ecoquest_test) | Insert duplicate completion directly | IntegrityError raised | As expected | Passed |
| TC-36 | Recycling Hero badge | Fresh seeded test database (ecoquest_test) | Complete 5 waste-management challenges | Recycling Hero awarded | As expected | Passed |
| TC-37 | Inactive challenge | Fresh seeded test database (ecoquest_test) | Deactivate challenge 2; POST complete | HTTP 404 | As expected | Passed |
| TC-38 | Teacher creates quiz and question | Fresh seeded test database (ecoquest_test) | POST quiz, then POST question with 4 options | Quiz, question and 4 options stored; correct option saved | As expected | Passed |
| TC-39 | Incomplete question rejected | Fresh seeded test database (ecoquest_test) | POST question with missing options | No question stored | As expected | Passed |
| TC-40 | Teacher creates challenge | Fresh seeded test database (ecoquest_test) | POST /teacher/challenges | Challenge stored with chosen XP | As expected | Passed |
| TC-41 | Teacher pages render | Fresh seeded test database (ecoquest_test) | GET teacher dashboard/students/quizzes/challenges/student detail/leaderboard | All HTTP 200 | As expected | Passed |
| TC-42 | Admin creates teacher | Fresh seeded test database (ecoquest_test) | POST /admin/users | Teacher role; password hashed | As expected | Passed |
| TC-43 | Admin self-protection | Fresh seeded test database (ecoquest_test) | POST delete and toggle on own id | Admin still exists and active | As expected | Passed |
| TC-44 | Admin topic/lesson CRUD and cascade | Fresh seeded test database (ecoquest_test) | Create topic+lesson; delete topic | Lesson deleted via ON DELETE CASCADE | As expected | Passed |
| TC-45 | Seed data volume and integrity | Fresh seeded test database (ecoquest_test) | Count seeded rows; check every question has 4 options, 1 correct | Counts meet minimums; integrity holds | As expected | Passed |
| TC-46 | Referential integrity | Fresh seeded test database (ecoquest_test) | Insert quiz_attempt with non-existent user | IntegrityError raised | As expected | Passed |
| TC-47 | Student pages render (incl. new student with no activity) | Fresh seeded test database (ecoquest_test) | GET 14 student-facing pages as student | All HTTP 200 | As expected | Passed |
| TC-48 | Teacher pages render | Fresh seeded test database (ecoquest_test) | GET 7 teacher pages as teacher | All HTTP 200 | As expected | Passed |
| TC-49 | Admin pages render | Fresh seeded test database (ecoquest_test) | GET admin pages and all teacher pages as admin | All HTTP 200 | As expected | Passed |
| TC-50 | Custom 404 page | Fresh seeded test database (ecoquest_test) | GET /no-such-page | HTTP 404 with friendly message | As expected | Passed |
| TC-51 | Mini-game pages | Fresh seeded test database (ecoquest_test) | GET /games/, /games/waste-sort, unknown game | 200, 200, 404 | As expected | Passed |
| TC-52 | Perfect game round | Fresh seeded test database (ecoquest_test) | Start Waste Sorting round, submit all correct | 8x5 + 10 XP and Game On badge | As expected | Passed |
| TC-53 | Daily XP cap for games | Fresh seeded test database (ecoquest_test) | Play the same game twice | Second round shows practice message; XP not doubled | As expected | Passed |
| TC-54 | Wrong game answers | Fresh seeded test database (ecoquest_test) | Submit all wrong bins | 0/8 and 0 XP | As expected | Passed |
| TC-55 | Game submit without a round | Fresh seeded test database (ecoquest_test) | POST finish without starting | Redirect; no XP | As expected | Passed |
| TC-56 | Game grading unit test | Fresh seeded test database (ecoquest_test) | grade_game and game_xp with mixed/invalid answers | Correct score, invalid bin counts as unanswered, XP formula | As expected | Passed |
| TC-57 | Quiz instant feedback lock | Fresh seeded test database (ecoquest_test) | Check a wrong option, check the right one, submit the right one | First choice stays locked and is graded | As expected | Passed |
| TC-58 | Quiz check validation | Fresh seeded test database (ecoquest_test) | Send an option from another question | HTTP 400 | As expected | Passed |
| TC-59 | Eco City stages | Fresh seeded test database (ecoquest_test) | city_stage for levels 1, 5, 10 | Pollution 95/55/5; names and air quality change | As expected | Passed |
| TC-60 | Daily quests bonus | Fresh seeded test database (ecoquest_test) | Do lesson, challenge, quiz, game in one day | Quest bonus awarded once; total XP matches | As expected | Passed |

## What is NOT covered by automated tests

* Visual layout/responsiveness — checked manually in the browser (see TEST_RESULTS.md, manual checks).
* Chart.js rendering — checked manually; charts load Chart.js from a CDN so they need internet access.
* Cloud deployment — not performed (see deployment.md).
* Performance/load testing — not performed.
