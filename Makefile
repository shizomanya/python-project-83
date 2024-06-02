install:
	poetry install
lint:
	poetry run flake8 page_analyzer
check:
	poetry check
dev:
	poetry run flask --app page_analyzer:app --debug run
start:
	poetry run gunicorn --workers=5 --bind=0.0.0.0:$(PORT) page_analyzer:app
connect:
	psql page_analyzer
database: 
	db-create schema-load
build:
	./build.sh
PORT ?= 8000
