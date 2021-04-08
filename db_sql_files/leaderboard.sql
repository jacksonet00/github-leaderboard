CREATE TABLE `leaderboard` (
	`id` SERIAL,
	`name` TEXT NOT NULL UNIQUE,
	`start` TIMESTAMP NOT NULL DEFAULT NOW(),
	`end` TIMESTAMP NOT NULL DEFAULT (NOW() + interval '1 week'),
	`repo_url` TEXT NOT NULL,
	`owner` INT NOT NULL,
	`results` INT,
	`last_update` TIMESTAMPTZ NOT NULL DEFAULT NOW(),

	PRIMARY KEY(`id`),
	FOREIGN KEY(`owner`) REFERENCES `user`(`id`),
	FOREIGN KEY(`results`) REFERENCES `result`(`id`)
);

CREATE OR REPLACE FUNCTION trigger_set_timestamp()
RETURNS TRIGGER AS $$
BEGIN
  NEW.last_update = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER set_timestamp
BEFORE UPDATE ON `leaderboard`
FOR EACH ROW
EXECUTE trigger_set_timestamp();
