/* CREATE EXTENSION citext; */


CREATE TABLE IF NOT EXISTS tickets
(
  ticket_id SERIAL NOT NULL,
  create_date TIMESTAMP,
  change_date TIMESTAMP,
  subject TEXT,
  text TEXT,
  email citext UNIQUE,
  state TEXT,
  FOREIGN KEY (ticket_id) REFERENCES Comments(ticket_id)
);


CREATE TABLE IF NOT EXISTS comments
(
  comment_id SERIAL NOT NULL,
  ticket_id SERIAL NOT NULL,
  create_date TIMESTAMP,
  email citext UNIQUE,
  text TEXT,
  FOREIGN KEY (ticket_id) REFERENCES Tickets(ticket_id)
);