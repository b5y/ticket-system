-- read before running server

CREATE TABLE IF NOT EXISTS tickets
(
  id          INTEGER PRIMARY KEY,
  create_date DATE,
  change_date DATE,
  subject     TEXT,
  text        TEXT,
  email       TEXT UNIQUE,
  state       TEXT
);


CREATE TABLE IF NOT EXISTS comments
(
  id          INTEGER PRIMARY KEY,
  ticket_id   INTEGER NOT NULL,
  create_date DATE,
  email       TEXT UNIQUE,
  text        TEXT,
  FOREIGN KEY (ticket_id) REFERENCES tickets (id)
);