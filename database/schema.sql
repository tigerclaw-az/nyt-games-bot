CREATE TABLE IF NOT EXISTS `users` (
  `user_id` VARCHAR(50) PRIMARY KEY,
  `name` VARCHAR(255) NOT NULL UNIQUE,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS `connections` (
  `puzzle_id` INT,
  `user_id` VARCHAR(50),
  `puzzle_str` TEXT NOT NULL,
  `score` INT NOT NULL,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`puzzle_id`, `user_id`),
  FOREIGN KEY (`user_id`) REFERENCES `users`(`user_id`) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS `strands` (
  `puzzle_id` INT,
  `user_id` VARCHAR(50),
  `puzzle_str` TEXT NOT NULL,
  `hints` INT NOT NULL,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`puzzle_id`, `user_id`),
  FOREIGN KEY (`user_id`) REFERENCES `users`(`user_id`) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS `wordle` (
  `puzzle_id` INT,
  `user_id` VARCHAR(50),
  `puzzle_str` TEXT NOT NULL,
  `score` INT NOT NULL,
  `green` INT NOT NULL,
  `yellow` INT NOT NULL,
  `other` INT NOT NULL,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`puzzle_id`, `user_id`),
  FOREIGN KEY (`user_id`) REFERENCES `users`(`user_id`) ON DELETE CASCADE
);
