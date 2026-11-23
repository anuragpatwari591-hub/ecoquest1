-- EcoQuest database schema (MySQL 8)
-- Run:  mysql -u root -p < database/schema.sql   (or use init_db.py)

CREATE TABLE IF NOT EXISTS roles (
    role_id   INT AUTO_INCREMENT PRIMARY KEY,
    role_name VARCHAR(20) NOT NULL UNIQUE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS users (
    user_id       INT AUTO_INCREMENT PRIMARY KEY,
    name          VARCHAR(100) NOT NULL,
    email         VARCHAR(120) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role_id       INT NOT NULL,
    institution   VARCHAR(120) DEFAULT NULL,
    class_name    VARCHAR(50)  DEFAULT NULL,
    total_xp      INT NOT NULL DEFAULT 0,
    streak        INT NOT NULL DEFAULT 0,
    last_active   DATE DEFAULT NULL,
    is_active     TINYINT(1) NOT NULL DEFAULT 1,
    created_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (role_id) REFERENCES roles(role_id),
    INDEX idx_users_xp (total_xp),
    INDEX idx_users_role (role_id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS topics (
    topic_id    INT AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(80) NOT NULL UNIQUE,
    icon        VARCHAR(10) NOT NULL DEFAULT '🌍',
    description TEXT NOT NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS lessons (
    lesson_id    INT AUTO_INCREMENT PRIMARY KEY,
    topic_id     INT NOT NULL,
    title        VARCHAR(150) NOT NULL,
    difficulty   ENUM('Beginner','Intermediate','Advanced') NOT NULL DEFAULT 'Beginner',
    introduction TEXT NOT NULL,
    explanation  TEXT NOT NULL,
    key_points   TEXT NOT NULL,          -- one point per line
    eco_tip      VARCHAR(300) NOT NULL,
    FOREIGN KEY (topic_id) REFERENCES topics(topic_id) ON DELETE CASCADE,
    INDEX idx_lessons_topic (topic_id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS quizzes (
    quiz_id     INT AUTO_INCREMENT PRIMARY KEY,
    topic_id    INT NOT NULL,
    title       VARCHAR(150) NOT NULL,
    description TEXT NOT NULL,
    difficulty  ENUM('Beginner','Intermediate','Advanced') NOT NULL DEFAULT 'Beginner',
    created_by  INT DEFAULT NULL,
    FOREIGN KEY (topic_id) REFERENCES topics(topic_id) ON DELETE CASCADE,
    FOREIGN KEY (created_by) REFERENCES users(user_id) ON DELETE SET NULL,
    INDEX idx_quizzes_topic (topic_id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS questions (
    question_id   INT AUTO_INCREMENT PRIMARY KEY,
    quiz_id       INT NOT NULL,
    question_text VARCHAR(500) NOT NULL,
    explanation   VARCHAR(500) DEFAULT NULL,
    FOREIGN KEY (quiz_id) REFERENCES quizzes(quiz_id) ON DELETE CASCADE,
    INDEX idx_questions_quiz (quiz_id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS options (
    option_id   INT AUTO_INCREMENT PRIMARY KEY,
    question_id INT NOT NULL,
    option_text VARCHAR(300) NOT NULL,
    is_correct  TINYINT(1) NOT NULL DEFAULT 0,
    FOREIGN KEY (question_id) REFERENCES questions(question_id) ON DELETE CASCADE,
    INDEX idx_options_question (question_id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS quiz_attempts (
    attempt_id      INT AUTO_INCREMENT PRIMARY KEY,
    user_id         INT NOT NULL,
    quiz_id         INT NOT NULL,
    score           INT NOT NULL,
    total_questions INT NOT NULL,
    xp_earned       INT NOT NULL DEFAULT 0,
    attempted_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (quiz_id) REFERENCES quizzes(quiz_id) ON DELETE CASCADE,
    INDEX idx_attempts_user (user_id),
    INDEX idx_attempts_quiz (quiz_id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS quiz_answers (
    answer_id          INT AUTO_INCREMENT PRIMARY KEY,
    attempt_id         INT NOT NULL,
    question_id        INT NOT NULL,
    selected_option_id INT DEFAULT NULL,
    is_correct         TINYINT(1) NOT NULL DEFAULT 0,
    FOREIGN KEY (attempt_id) REFERENCES quiz_attempts(attempt_id) ON DELETE CASCADE,
    FOREIGN KEY (question_id) REFERENCES questions(question_id) ON DELETE CASCADE,
    FOREIGN KEY (selected_option_id) REFERENCES options(option_id) ON DELETE SET NULL,
    INDEX idx_answers_attempt (attempt_id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS challenges (
    challenge_id INT AUTO_INCREMENT PRIMARY KEY,
    topic_id     INT NOT NULL,
    title        VARCHAR(150) NOT NULL,
    description  TEXT NOT NULL,
    difficulty   ENUM('Easy','Medium','Hard') NOT NULL DEFAULT 'Easy',
    xp_reward    INT NOT NULL DEFAULT 20,
    is_active    TINYINT(1) NOT NULL DEFAULT 1,
    created_by   INT DEFAULT NULL,
    FOREIGN KEY (topic_id) REFERENCES topics(topic_id) ON DELETE CASCADE,
    FOREIGN KEY (created_by) REFERENCES users(user_id) ON DELETE SET NULL,
    INDEX idx_challenges_topic (topic_id)
) ENGINE=InnoDB;

-- One completion per student per challenge per day (a challenge can be repeated on another day)
CREATE TABLE IF NOT EXISTS challenge_completions (
    completion_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id       INT NOT NULL,
    challenge_id  INT NOT NULL,
    completed_on  DATE NOT NULL,
    xp_earned     INT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (challenge_id) REFERENCES challenges(challenge_id) ON DELETE CASCADE,
    UNIQUE KEY uq_user_challenge_day (user_id, challenge_id, completed_on)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS badges (
    badge_id    INT AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(60) NOT NULL UNIQUE,
    description VARCHAR(255) NOT NULL,
    icon        VARCHAR(10) NOT NULL DEFAULT '🏅',
    rule_type   VARCHAR(30) NOT NULL,   -- lessons, quizzes, topic_challenges, topic_lessons, streak, xp
    rule_value  INT NOT NULL,
    topic_id    INT DEFAULT NULL,       -- used by topic-specific rules
    FOREIGN KEY (topic_id) REFERENCES topics(topic_id) ON DELETE SET NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS user_badges (
    user_id   INT NOT NULL,
    badge_id  INT NOT NULL,
    earned_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, badge_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (badge_id) REFERENCES badges(badge_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- A row means "this user completed this lesson" (lesson-level progress)
CREATE TABLE IF NOT EXISTS user_progress (
    progress_id  INT AUTO_INCREMENT PRIMARY KEY,
    user_id      INT NOT NULL,
    lesson_id    INT NOT NULL,
    completed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (lesson_id) REFERENCES lessons(lesson_id) ON DELETE CASCADE,
    UNIQUE KEY uq_user_lesson (user_id, lesson_id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS activity_log (
    log_id      INT AUTO_INCREMENT PRIMARY KEY,
    user_id     INT NOT NULL,
    activity    VARCHAR(30) NOT NULL,   -- lesson, quiz, challenge, badge
    description VARCHAR(255) NOT NULL,
    xp_change   INT NOT NULL DEFAULT 0,
    created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    INDEX idx_log_user (user_id, created_at)
) ENGINE=InnoDB;

-- Teacher/admin announcements shown on the student dashboard
CREATE TABLE IF NOT EXISTS announcements (
    announcement_id INT AUTO_INCREMENT PRIMARY KEY,
    title      VARCHAR(120) NOT NULL,
    message    VARCHAR(500) NOT NULL,
    created_by INT DEFAULT NULL,
    is_active  TINYINT(1) NOT NULL DEFAULT 1,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(user_id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- Latest live air-quality readings (Eco Pulse), kept so the page works offline
CREATE TABLE IF NOT EXISTS air_readings (
    reading_id  INT AUTO_INCREMENT PRIMARY KEY,
    city        VARCHAR(40) NOT NULL,
    observed_at DATETIME NOT NULL,
    us_aqi      INT NOT NULL,
    pm2_5       DECIMAL(6,1) DEFAULT NULL,
    pm10        DECIMAL(6,1) DEFAULT NULL,
    fetched_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_city_time (city, observed_at)
) ENGINE=InnoDB;
