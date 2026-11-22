# Database Design (MySQL 8, InnoDB)

The authoritative definition is [`database/schema.sql`](../database/schema.sql). This document and the ER diagram match it.
Demo content is loaded by `init_db.py` from `database/seed_data.py` (Python was chosen over a raw `seed.sql` so that demo
passwords can be hashed with the same code the application uses).

## ER Diagram

```mermaid
erDiagram
    roles ||--o{ users : "has"
    users ||--o{ quiz_attempts : "makes"
    users ||--o{ challenge_completions : "completes"
    users ||--o{ user_progress : "tracks"
    users ||--o{ activity_log : "generates"
    users ||--o{ user_badges : "earns"
    badges ||--o{ user_badges : "awarded as"
    topics ||--o{ lessons : "contains"
    topics ||--o{ quizzes : "contains"
    topics ||--o{ challenges : "categorises"
    topics |o--o{ badges : "topic rule (optional)"
    quizzes ||--o{ questions : "has"
    questions ||--o{ options : "has 4"
    quizzes ||--o{ quiz_attempts : "attempted in"
    quiz_attempts ||--o{ quiz_answers : "records"
    questions ||--o{ quiz_answers : "answered in"
    options |o--o{ quiz_answers : "selected"
    lessons ||--o{ user_progress : "completed in"
    challenges ||--o{ challenge_completions : "completed in"
    users |o--o{ quizzes : "created_by"
    users |o--o{ challenges : "created_by"

    roles { int role_id PK
            string role_name UK }
    users { int user_id PK
            string name
            string email UK
            string password_hash
            int role_id FK
            string institution
            string class_name
            int total_xp
            int streak
            date last_active
            bool is_active
            timestamp created_at }
    topics { int topic_id PK
             string name UK
             string icon
             text description }
    lessons { int lesson_id PK
              int topic_id FK
              string title
              enum difficulty
              text introduction
              text explanation
              text key_points
              string eco_tip }
    quizzes { int quiz_id PK
              int topic_id FK
              string title
              text description
              int created_by FK }
    questions { int question_id PK
                int quiz_id FK
                string question_text
                string explanation }
    options { int option_id PK
              int question_id FK
              string option_text
              bool is_correct }
    quiz_attempts { int attempt_id PK
                    int user_id FK
                    int quiz_id FK
                    int score
                    int total_questions
                    int xp_earned
                    timestamp attempted_at }
    quiz_answers { int answer_id PK
                   int attempt_id FK
                   int question_id FK
                   int selected_option_id FK
                   bool is_correct }
    challenges { int challenge_id PK
                 int topic_id FK
                 string title
                 text description
                 enum difficulty
                 int xp_reward
                 bool is_active
                 int created_by FK }
    challenge_completions { int completion_id PK
                            int user_id FK
                            int challenge_id FK
                            date completed_on
                            int xp_earned }
    badges { int badge_id PK
             string name UK
             string description
             string icon
             string rule_type
             int rule_value
             int topic_id FK }
    user_badges { int user_id PK,FK
                  int badge_id PK,FK
                  timestamp earned_at }
    user_progress { int progress_id PK
                    int user_id FK
                    int lesson_id FK
                    timestamp completed_at }
    activity_log { int log_id PK
                   int user_id FK
                   string activity
                   string description
                   int xp_change
                   timestamp created_at }
```

## Relationships (cardinality)

| Relationship | Cardinality | Implemented by |
|---|---|---|
| Role – User | 1:N | `users.role_id` |
| User – QuizAttempt | 1:N | `quiz_attempts.user_id` |
| Quiz – Question | 1:N | `questions.quiz_id` |
| Question – Option | 1:N (4 per question, 1 correct) | `options.question_id` |
| Topic – Lesson / Quiz / Challenge | 1:N | `lessons/quizzes/challenges.topic_id` |
| User – ChallengeCompletion – Challenge | 1:N each | `challenge_completions` |
| User – Badge | N:M | `user_badges` (composite primary key) |
| User – Lesson (progress) | N:M | `user_progress` (unique user+lesson) |

## Constraints worth knowing

* `users.email` UNIQUE; passwords stored only as Werkzeug hashes (`password_hash`).
* `challenge_completions` UNIQUE(`user_id`,`challenge_id`,`completed_on`): a challenge can be completed once per student per day.
* `user_progress` UNIQUE(`user_id`,`lesson_id`): a lesson can be completed once.
* `user_badges` PRIMARY KEY(`user_id`,`badge_id`): a badge can be earned once.
* Foreign keys use `ON DELETE CASCADE` for dependent data (e.g. deleting a topic removes its lessons, quizzes, questions, options)
  and `ON DELETE SET NULL` for optional links (`created_by`, `selected_option_id`).
* Indexes: on foreign keys used in joins and on `users.total_xp` (leaderboard sort).

## Normalization

* **1NF** – every column holds a single value. Exception chosen deliberately: `lessons.key_points` stores several
  short bullet points as newline-separated text, because they are only ever displayed together (a separate table would add
  complexity without benefit for this project).
* **2NF / 3NF** – every non-key column depends on the whole key and only on the key: roles are in their own table, quiz
  data is split into quiz → question → option, completions are in separate tables. `users.total_xp` and `users.streak` are
  deliberate **denormalised, derived values** kept for fast leaderboard queries (the history in `activity_log` records each change).

## Badge rule types (`badges.rule_type`)

| rule_type | Meaning |
|---|---|
| `lessons` | number of lessons completed ≥ rule_value |
| `quizzes` | number of quiz attempts ≥ rule_value |
| `topic_challenges` | challenges completed in `topic_id` ≥ rule_value |
| `topic_activity` | lessons + challenges completed in `topic_id` ≥ rule_value |
| `streak` | current streak ≥ rule_value |
| `xp` | total XP ≥ rule_value |

## Example queries used by the application

```sql
-- Leaderboard (SQL sorting)
SELECT u.name, u.total_xp FROM users u JOIN roles r ON u.role_id = r.role_id
WHERE r.role_name = 'student' ORDER BY u.total_xp DESC;

-- Average score per quiz (teacher dashboard)
SELECT q.title, ROUND(AVG(a.score * 100 / a.total_questions)) AS avg_pct
FROM quizzes q LEFT JOIN quiz_attempts a ON q.quiz_id = a.quiz_id GROUP BY q.quiz_id, q.title;
```
