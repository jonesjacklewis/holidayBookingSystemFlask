CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS emails (
    email_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    email TEXT NOT NULL UNIQUE,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE IF NOT EXISTS holiday_allowance (
    holiday_allowance_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    holiday_allowance INTEGER NOT NULL DEFAULT 27,
    remaining_holiday_allowance INTEGER NOT NULL DEFAULT 27,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE IF NOT EXISTS holidays (
    holiday_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    date DATE NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
    UNIQUE (user_id, date)
);

INSERT OR IGNORE INTO users (user_id, username) VALUES (1, 'testuser');
INSERT OR IGNORE INTO emails (email_id, user_id, email) VALUES (1, 1, 'test.user@domain.com');
INSERT OR IGNORE INTO holiday_allowance (holiday_allowance_id, user_id, holiday_allowance, remaining_holiday_allowance) VALUES (1, 1, 27, 27);