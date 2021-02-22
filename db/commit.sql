CREATE TABLE `commit` (
	`id` SERIAL,
	`user_id` INT,
	`commit_count` INT,
	`last_update` TIMESTAMPTZ NOT NULL DEFAULT NOW(),

	PRIMARY KEY(`id`)
);

CREATE OR REPLACE FUNCTION trigger_set_timestamp()
RETURNS TRIGGER AS $$
BEGIN
  NEW.last_update = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER set_timestamp
BEFORE UPDATE ON `commit`
FOR EACH ROW
EXECUTE trigger_set_timestamp();