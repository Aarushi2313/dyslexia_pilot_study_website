-- ============================================================
-- Run this SQL to set up the Listening Task database entries
-- ============================================================

-- 1. Add 'Listening Task' to the tasks master table
INSERT IGNORE INTO tasks (task_name, description, estimated_time)
VALUES (
  'Listening Task',
  'Listen to an audio clip and answer comprehension questions.',
  10
);

-- 2. Create the listening_tasks table for class-wise listening questions
CREATE TABLE IF NOT EXISTS listening_tasks (
  id              INT NOT NULL AUTO_INCREMENT,
  task_name       VARCHAR(255) NOT NULL,
  class_level     INT NOT NULL,
  difficulty_level ENUM('Easy','Medium','Hard') NOT NULL,
  audio_url       VARCHAR(500) DEFAULT NULL,
  question1       TEXT NOT NULL,
  question2       TEXT NOT NULL,
  question3       TEXT NOT NULL,
  answer1_options JSON DEFAULT NULL,
  answer2_options JSON DEFAULT NULL,
  answer3_type    ENUM('text','multiple_choice') DEFAULT 'text',
  answer1         TEXT,
  answer2         TEXT,
  instructions    TEXT,
  estimated_time  INT DEFAULT 5,
  created_at      TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  CONSTRAINT listening_tasks_chk_1 CHECK (class_level BETWEEN 1 AND 12)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 3. Create/upgrade the listening_progress table for saving/submitting answers
CREATE TABLE IF NOT EXISTS listening_progress (
  id           INT AUTO_INCREMENT PRIMARY KEY,
  attempt_id   INT NOT NULL,
  q1           TEXT,
  q2           VARCHAR(255) DEFAULT NULL,
  q3           TEXT,
  status       ENUM('In Progress','Completed') DEFAULT 'In Progress',
  updated_at   TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  score        INT DEFAULT 0,
  max_score    INT DEFAULT 2,
  UNIQUE KEY uq_listening_attempt (attempt_id),
  FOREIGN KEY (attempt_id) REFERENCES user_task_attempts(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 4. Upgrade older listening_progress tables in place if they already exist
ALTER TABLE listening_progress
  ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  ADD COLUMN IF NOT EXISTS score INT DEFAULT 0,
  ADD COLUMN IF NOT EXISTS max_score INT DEFAULT 2;
