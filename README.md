# PAGE ANALYZER
## Description:
[Page Analyzer](https://python-project-lvl3-morl.onrender.com) is a web application that checks web pages for SEO suitability. By running the check, you can get basic information from the main page of the site.
### Hexlet tests and linter status:
[![Actions Status](https://github.com/shizomanya/python-project-83/actions/workflows/hexlet-check.yml/badge.svg)](https://github.com/shizomanya/python-project-83/actions)

[![Python CI](https://github.com/shizomanya/python-project-lvl3/actions/workflows/ci.yml/badge.svg)](https://github.com/shizomanya/python-project-lvl3/actions/workflows/ci.yml)

<a href="https://codeclimate.com/github/shizomanya/python-project-lvl3/maintainability"><img src="https://api.codeclimate.com/v1/badges/fc423b38c73510c221a2/maintainability" /></a>

## Requirements:
App developed with:
```
poetry = "1.8.3"
python = "^3.10"
flake8 = "^7.0.0"
gunicorn = "^22.0.0"
python-dotenv = "^1.0.1"
psycopg2-binary = "^2.9.9"
flask = "^3.0.3"
requests = "^2.32.2"
beautifulsoup4 = "^4.12.3"
validators = "^0.28.3"
playwright = "1.42.0"
flask-migrate = "^4.0.7"
sqlalchemy = "^2.0.30"
```
## Installation Instruction:
### Clone the current repository:
```
$ python3 -m pip install git+https://github.com/shizomanya/python-project-lvl3
```
### Makefile commands:
Install poetry project: ```make install```

Install poetry project and start postgresql server: ```make build```

Run flask app: ```make dev```

Start gunicorn server: ```make start```

## How to use this App:
1. Open the main page of the application.
2. Enter the address of the web page you want to check.
3. Run the analyzer test.
4. You can get information from the main page of the site by clicking on the “Run check” button. The result with the response code, h1 tag, title, description and creation date will appear if the test is successful.
5. All checks can be viewed in the “websites” tab.