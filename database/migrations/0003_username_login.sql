BEGIN;

ALTER TABLE app_users RENAME COLUMN email TO username;

COMMIT;
