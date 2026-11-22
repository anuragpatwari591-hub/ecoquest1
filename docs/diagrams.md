# UML and Data Flow Diagrams

All diagrams are written in Mermaid (rendered automatically by GitHub and VS Code Markdown preview) and describe only
features that exist in the implemented application.

## DFD Level 0 (context diagram)

```mermaid
flowchart LR
    S[/Student/] -- "registration, login, lesson & quiz & challenge actions" --> P(("0<br/>EcoQuest<br/>System"))
    P -- "lessons, quiz results, XP, badges, leaderboard, progress" --> S
    T[/Teacher/] -- "login, quizzes, questions, challenges" --> P
    P -- "student performance, class analytics" --> T
    A[/Admin/] -- "users, topics, lessons, badges, content" --> P
    P -- "platform statistics, reports" --> A
```

## DFD Level 1

```mermaid
flowchart TB
    S[/Student/]; T[/Teacher/]; A[/Admin/]
    P1(("1.0<br/>Authenticate<br/>& authorise"))
    P2(("2.0<br/>Learning<br/>module"))
    P3(("3.0<br/>Quiz<br/>module"))
    P4(("4.0<br/>Challenge<br/>module"))
    P5(("5.0<br/>Gamification<br/>XP/level/streak/badges"))
    P6(("6.0<br/>Analytics &<br/>leaderboard"))
    P7(("7.0<br/>Content & user<br/>management"))
    D1[("D1 users, roles")]
    D2[("D2 topics, lessons,<br/>user_progress")]
    D3[("D3 quizzes, questions,<br/>options, attempts, answers")]
    D4[("D4 challenges,<br/>completions")]
    D5[("D5 badges, user_badges,<br/>activity_log")]
    S & T & A -- credentials --> P1
    P1 <--> D1
    S -- "open/complete lesson" --> P2
    P2 <--> D2
    P2 -- "lesson completed" --> P5
    S -- "answers" --> P3
    P3 <--> D3
    P3 -- "score" --> P5
    S -- "complete challenge" --> P4
    P4 <--> D4
    P4 -- "XP reward" --> P5
    P5 <--> D1
    P5 <--> D5
    P5 -- "XP, level, badges" --> S
    D1 & D2 & D3 & D4 & D5 --> P6
    P6 -- "leaderboard, progress" --> S
    P6 -- "class analytics" --> T
    T -- "new quiz/question/challenge" --> P7
    A -- "manage users, topics, lessons, badges" --> P7
    P7 --> D1 & D2 & D3 & D4 & D5
    P6 -- "platform statistics" --> A
```

## Use case diagram

```mermaid
flowchart LR
    S((Student)); T((Teacher)); A((Admin))
    subgraph EcoQuest
      U1[Register / Login / Logout]
      U2[Read & complete lessons]
      U3[Take quizzes, view results]
      U4[Complete challenges]
      U5[View leaderboard & progress]
      U6[Manage profile]
      U7[Create quizzes & questions]
      U8[Create challenges]
      U9[View students & class analytics]
      U10[Manage users]
      U11[Manage topics, lessons, badges]
      U12[View platform statistics]
    end
    S --- U1 & U2 & U3 & U4 & U5 & U6
    T --- U1 & U7 & U8 & U9 & U5
    A --- U1 & U10 & U11 & U12 & U7 & U8
```

## Class diagram

The implementation uses a modular, function-based style (Flask blueprints and helper modules) rather than custom Python
classes, so the class diagram shows the **domain entities** (which map one-to-one to database tables) and the modules that
operate on them.

```mermaid
classDiagram
    direction TB
    class User {
      +user_id
      +name
      +email
      +password_hash
      +role
      +total_xp
      +streak
    }
    class Topic { +topic_id +name }
    class Lesson { +title +difficulty }
    class Quiz { +quiz_id +title }
    class Question { +question_text }
    class Option { +option_text +is_correct }
    class QuizAttempt { +score +xp_earned }
    class Challenge { +title +xp_reward }
    class ChallengeCompletion { +completed_on }
    class Badge { +name +rule_type +rule_value }
    class gamification_module {
      +calculate_level()
      +calculate_quiz_xp()
      +next_streak()
      +record_activity()
      +check_badges()
      +daily_quests()
      +city_stage()
      +leaderboard()
    }
    class auth_module {
      +hash_password()
      +authenticate()
      +login_required()
    }
    Topic "1" o-- "*" Lesson
    Topic "1" o-- "*" Quiz
    Topic "1" o-- "*" Challenge
    Quiz "1" *-- "*" Question
    Question "1" *-- "4" Option
    User "1" -- "*" QuizAttempt
    Quiz "1" -- "*" QuizAttempt
    User "1" -- "*" ChallengeCompletion
    Challenge "1" -- "*" ChallengeCompletion
    User "*" -- "*" Badge : user_badges
    gamification_module ..> User
    gamification_module ..> Badge
    auth_module ..> User
```

## Sequence diagram — submitting a quiz

```mermaid
sequenceDiagram
    actor S as Student
    participant B as Browser
    participant F as Flask (routes/quiz.py)
    participant G as gamification.py
    participant DB as MySQL
    S->>B: Answer questions, click Submit
    B->>F: POST /quiz/3/submit (answers, csrf_token)
    F->>F: check_csrf, login_required("student")
    F->>DB: SELECT questions + options
    F->>F: grade() -> score
    F->>G: calculate_quiz_xp(score, total)
    F->>DB: INSERT quiz_attempts, quiz_answers
    F->>G: record_activity()
    G->>DB: UPDATE users.total_xp, INSERT activity_log
    G->>DB: update streak (+7-day bonus)
    G->>DB: check_badges -> INSERT user_badges
    F->>DB: COMMIT
    F-->>B: 302 redirect to /quiz/result/{id}
    B->>F: GET result page
    F-->>B: Score, accuracy, XP, answer review
```

## Sequence diagram — login

```mermaid
sequenceDiagram
    actor U as User
    participant F as Flask (routes/auth.py)
    participant DB as MySQL
    U->>F: POST /login (email, password)
    F->>DB: SELECT user JOIN roles WHERE email=%s
    F->>F: check_password_hash(hash, password)
    alt valid and active
        F->>F: session = user_id, name, role
        F-->>U: redirect to role dashboard
    else invalid
        F-->>U: 401 "Invalid email or password"
    end
```

## Activity diagram — completing an eco challenge

```mermaid
flowchart TD
    A([Student opens Challenges]) --> B[Select a challenge]
    B --> C{Challenge active?}
    C -- No --> X([Not available - 404])
    C -- Yes --> D{Already completed today?}
    D -- Yes --> E([Message: come back tomorrow])
    D -- No --> F[Save completion, add XP, update streak]
    F --> G[Check streak bonus, daily quests and badges]
    G --> H[Commit to database]
    H --> I([Show XP, level-up and new badges])
```
