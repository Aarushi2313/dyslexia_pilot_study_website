INSERT IGNORE INTO tasks (task_name, description, estimated_time)
VALUES (
  'Visual Task',
  'View an image or visual and answer comprehension or observation questions.',
  10
);

CREATE TABLE IF NOT EXISTS visual_tasks (
  id                INT NOT NULL AUTO_INCREMENT,
  task_name         VARCHAR(255) NOT NULL,
  class_level       INT NOT NULL,
  difficulty_level  ENUM('Easy','Medium','Hard') NOT NULL,
  image_url         VARCHAR(500) DEFAULT NULL,
  question1         TEXT NOT NULL,
  question2         TEXT NOT NULL,
  question3         TEXT NOT NULL,
  answer1_options   JSON DEFAULT NULL,
  answer2_options   JSON DEFAULT NULL,
  answer3_type      ENUM('text','multiple_choice') DEFAULT 'text',
  answer1           TEXT,
  answer2           TEXT,
  instructions      TEXT,
  estimated_time    INT DEFAULT 5,
  created_at        TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  CONSTRAINT visual_tasks_chk_1 CHECK (class_level BETWEEN 1 AND 12)
) ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4
COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS visual_progress (
  id            INT AUTO_INCREMENT PRIMARY KEY,
  attempt_id    INT NOT NULL,
  q1            TEXT,
  q2            VARCHAR(255) DEFAULT NULL,
  q3            TEXT,
  status        ENUM('In Progress','Completed') DEFAULT 'In Progress',
  updated_at    TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  score         INT DEFAULT 0,
  max_score     INT DEFAULT 2,
  UNIQUE KEY uq_visual_attempt (attempt_id),
  CONSTRAINT visual_progress_ibfk_1
    FOREIGN KEY (attempt_id) REFERENCES user_task_attempts(id) ON DELETE CASCADE
) ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4;
