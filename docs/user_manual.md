# EcoQuest User Manual

## Demo accounts (local demo data only)
| Role | Email | Password |
|---|---|---|
| Admin | admin@ecoquest.test | Admin@123 |
| Teacher | teacher@ecoquest.test | Teacher@123 |
| Student | student@ecoquest.test | Student@123 |
| Student (classmates with sample activity) | riya@ecoquest.test, kabir@ecoquest.test, sara@ecoquest.test | Student@123 |

These are fictional accounts created by `init_db.py`. Change them for any real deployment.

## Student guide
1. **Register / Login** – use *Register* on the home page (a student account), then *Login*.
2. **Dashboard** – shows XP, level, streak, badges, leaderboard position, topic-wise learning progress, today's challenge, available lessons/quizzes and recent activity.
3. **Learn** – open a topic, pick a lesson, read the introduction, explanation, key points and eco-tip, then press *Mark as complete* to earn **+10 XP**.
4. **Quizzes** – choose a quiz, read the instructions and press *Start quiz*. Answer using the radio buttons and the numbered question buttons; press *Submit quiz*. You earn **10 XP per correct answer** and **+50 XP** for a perfect score. The result page shows score, accuracy, XP and an answer review. All attempts are stored in your history.
5. **Challenges** – do the real-life action, then press *Mark complete* to earn the challenge XP. Each challenge can be completed once per day.
6. **Levels** – `Level = floor(XP / 100) + 1`. The dashboard bar shows progress to the next level.
7. **Streak** – any lesson, quiz or challenge counts as activity for the day. Activity on consecutive days increases the streak; missing a day resets it to 1. Reaching 7, 14, 21… days gives **+100 bonus XP**.
8. **Badges** – unlock automatically (see *Progress → Badges* for requirements).
9. **Leaderboard** – students ranked by XP; filter by institution or class.
10. **Progress** – charts for topic progress, quiz scores and XP per day, plus activity history.
11. **Profile** – edit your name, institution and class.

## Teacher guide
* **Dashboard** – totals, active students (activity in last 7 days), average quiz score, attempts, challenges completed, and four charts.
* **Students** – list with filters; *View* shows a student's XP, topic progress, badges, challenges and quiz attempts.
* **Quizzes** – create a quiz (title, topic, description), then add questions (four options, choose the correct one). You can delete questions and your own quizzes.
* **Challenges** – create challenges (title, category, difficulty, XP 1–200) and activate/deactivate them.

## Admin guide
* **Dashboard** – platform statistics and charts.
* **Users** – add students/teachers/admins, disable/enable, delete (not your own account).
* **Topics / Lessons / Badges** – create, edit and delete content. Badge rules are chosen from a list; badges are then awarded automatically.
* **Quizzes / Challenges / Analytics** – the admin can use all teacher pages.

## Troubleshooting
| Problem | Fix |
|---|---|
| "Invalid or missing form token" | Reload the page and submit the form again |
| Charts are empty | Check the internet connection (Chart.js is loaded from a CDN) |
| Cannot connect to database | Check MySQL is running and `.env` values are correct |
