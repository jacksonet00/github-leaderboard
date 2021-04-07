CREATE TABLE `user` (
	`id` SERIAL,
	`username` TEXT NOT NULL UNIQUE,
	`password` TEXT NOT NULL,
	`github_username` TEXT NOT NULL UNIQUE,
	`github_key` TEXT NOT NULL UNIQUE,

	PRIMARY KEY(`id`)
);
