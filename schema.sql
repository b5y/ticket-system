-- read before running server

DROP TABLE IF EXISTS tickets CASCADE;

CREATE TABLE IF NOT EXISTS tickets
(
  id          SERIAL PRIMARY KEY,
  create_date TIMESTAMP,
  change_date TIMESTAMP,
  subject     TEXT,
  _text_      TEXT,
  email       VARCHAR(254),
  state       TEXT
);


DROP TABLE IF EXISTS comments CASCADE;

CREATE TABLE IF NOT EXISTS comments
(
  id          SERIAL PRIMARY KEY,
  ticket_id   SERIAL,
  create_date TIMESTAMP,
  email       VARCHAR(254),
  _text_      TEXT,
  FOREIGN KEY (ticket_id) REFERENCES tickets (id)
);

GRANT ALL PRIVILEGES ON TABLE tickets TO postgres;
GRANT ALL PRIVILEGES ON TABLE comments TO postgres;