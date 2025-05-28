CREATE TABLE IF NOT EXISTS `users` (
  `user_id` INTEGER NOT NULL PRIMARY KEY,
  `name` VARCHAR(255) NOT NULL UNIQUE,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS `connections` (
  `puzzle_id` INTEGER,
  `user_id` INTEGER,
  `puzzle_str` TEXT NOT NULL,
  `score` INTEGER NOT NULL,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`puzzle_id`, `user_id`),
  FOREIGN KEY (`user_id`) REFERENCES `users`(`user_id`) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS `strands` (
  `puzzle_id` INTEGER,
  `user_id` INTEGER,
  `puzzle_str` TEXT NOT NULL,
  `hINTEGERs` INTEGER NOT NULL,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`puzzle_id`, `user_id`),
  FOREIGN KEY (`user_id`) REFERENCES `users`(`user_id`) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS `wordle` (
  `puzzle_id` INTEGER,
  `user_id` INTEGER,
  `puzzle_str` TEXT NOT NULL,
  `score` INTEGER NOT NULL,
  `green` INTEGER NOT NULL,
  `yellow` INTEGER NOT NULL,
  `other` INTEGER NOT NULL,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`puzzle_id`, `user_id`),
  FOREIGN KEY (`user_id`) REFERENCES `users`(`user_id`) ON DELETE CASCADE
);
