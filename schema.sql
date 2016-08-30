-- read before running server

DROP TABLE IF EXISTS tickets;

CREATE TABLE IF NOT EXISTS tickets
(
  id          SERIAL PRIMARY KEY,
  create_date DATE,
  change_date DATE,
  subject     TEXT,
  text        TEXT,
  email       VARCHAR(254),
  state       TEXT
);


DROP TABLE IF EXISTS comments;

CREATE TABLE IF NOT EXISTS comments
(
  id          SERIAL PRIMARY KEY,
  ticket_id   INTEGER NOT NULL,
  create_date DATE,
  email       VARCHAR(254),
  text        TEXT,
  FOREIGN KEY (ticket_id) REFERENCES tickets (id)
);