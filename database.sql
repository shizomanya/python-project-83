DROP TABLE IF EXISTS url_checks;
DROP TABLE IF EXISTS urls;

CREATE TABLE urls (
  id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  name VARCHAR(255) UNIQUE NOT NULL,
  created_at DATE NOT NULL,
  last_check DATE,
  status_code INTEGER
);

CREATE TABLE url_checks (
  id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  url_id BIGINT REFERENCES urls(id),
  status_code INTEGER,
  h1 TEXT,
  title TEXT,
  description TEXT,
  created_at DATE
);