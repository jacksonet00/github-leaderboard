CREATE TABLE `result` (
	`id` SERIAL,
	`user_id` INT,
	`leaderboard_id` INT,
	`score` INT,

	PRIMARY KEY(`id`),
	FOREIGN KEY(`user_id`) REFERENCES `user`(`id`),
	FOREIGN KEY(`leaderboard_id`) REFERENCES `leaderboard`(`id`)
);