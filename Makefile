all: start db-reset schema-load

schema-load:
	psql python-project-lvl3 < database.sql

db-create:
	createdb python-project-lvl3

db-reset:
	dropdb python-project-lvl3 || true
	createdb python-project-lvl3

connect:
	psql -d python-project-lvl3

dev:
	poetry run flask --app page_analyzer:app run

install:
	poetry install

lint:
	poetry run flake8 page_analyzer

check: 
	poetry check

sPORT ?= 8000
start:
	poetry run gunicorn -w 5 -b 0.0.0.0:$(PORT) page_analyzer:app

build:
	./build.sh
