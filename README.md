<div align="center">
<h1>Page Analyzer</h1>

<p>
Analyze specified pages for SEO suitability.
</p>

### Hexlet tests and linter status:
[![Actions Status](https://github.com/shizomanya/python-project-83/actions/workflows/hexlet-check.yml/badge.svg)](https://github.com/shizomanya/python-project-83/actions)
[![Python CI](https://github.com/shizomanya/python-project-lvl3/actions/workflows/ci.yml/badge.svg)](https://github.com/shizomanya/python-project-lvl3/actions/workflows/ci.yml)
<a href="https://codeclimate.com/github/shizomanya/python-project-lvl3/maintainability"><img src="https://api.codeclimate.com/v1/badges/fc423b38c73510c221a2/maintainability" /></a>

<p>
<a href="#about">About</a> •
<a href="#installation">Installation</a> •
<a href="#usage">Usage</a> 
</p>
</div>

<details><summary style="font-size:larger;"><b>Table of Contents</b></summary>

- [PAGE ANALYZER](#page-analyzer)
  - [About:](#about)
  - [Requirements:](#requirements)
    - [Makefile commands:](#makefile-commands)
  - [Installation:](#installation)
      - [Python](#python)
      - [Poetry](#poetry)
      - [PostgreSQL](#postgresql)
    - [Application](#application)
  - [Usage](#usage)
  - [How to use this App:](#how-to-use-this-app)

</details>

# PAGE ANALYZER
## About:
[Page Analyzer](https://python-project-lvl3-morl.onrender.com) is a web application that checks web pages for SEO suitability. By running the check, you can get basic information from the main page of the site.

## Requirements:
App developed with:
* [Python](https://www.python.org/)
* [Flask](https://flask.palletsprojects.com/en/2.2.x/)
* [Bootstrap 5](https://getbootstrap.com/)
* [PostgreSQL](https://www.postgresql.org/)
* [Beautiful Soup 4](https://www.crummy.com/software/BeautifulSoup/)
* [Jinja 2](https://palletsprojects.com/p/jinja/)
* [Psycopg 2](https://www.psycopg.org/)
* [Gunicorn](https://gunicorn.org/)
* [Poetry](https://python-poetry.org/)
* [pytest](https://docs.pytest.org/en/7.2.x/)
* [Flake8](https://flake8.pycqa.org/en/latest/)

### Makefile commands:
Install poetry project: ```make install```

Install poetry project and start postgresql server: ```make build```

Run flask app: ```make dev```

Start gunicorn server: ```make start```

## Installation:

#### Python

Before installing the package make sure you have Python version 3.10 or higher installed:

```bash
>> python --version
Python 3.10.12
```

#### Poetry

The project uses the Poetry dependency manager. To install Poetry use its [official instruction](https://python-poetry.org/docs/#installation).

#### PostgreSQL

As database the PostgreSQL database system is being used. You need to install it first. You can download the ready-to-use package from [official website](https://www.postgresql.org/download/) or use Homebrew:
```shell
>> brew install postgresql
```
### Application

To use the application, you need to clone the repository to your computer. This is done using the `git clone` command. Clone the project:

```bash
>> git clone https://github.com/shizomanya/python-project-lvl3.git && cd python-project-lvl3
```

Then you have to install all necessary dependencies:

```bash
>> make install
```

Create .env file in the root folder and add following variables:
```
DATABASE_URL = postgresql://{provider}://{user}:{password}@{host}:{port}/{db}
SECRET_KEY = '{your secret key}'
```
Run commands from `database.sql` to create the required tables.

---
## Usage

Start the gunicorn Flask server by running:
```bash
make start
```
By default, the server will be available at http://0.0.0.0:8000. 

_It is also possible to start it local in development mode with debugger active using:_
```bash
make dev
```
_The dev server will be at http://127.0.0.1:5000._

## How to use this App:
1. Open the main page of the application.
2. Enter the address of the web page you want to check.
3. Run the analyzer test.
4. You can get information from the main page of the site by clicking on the “Run check” button. The result with the response code, h1 tag, title, description and creation date will appear if the test is successful.
5. All checks can be viewed in the “websites” tab (You can see all added URLs on the `/urls` page.)
