import os
import sys
import datetime
import logging
import requests
import psycopg2
import psycopg2.extras
import bs4
from flask import Flask, request, flash, redirect, render_template, url_for
from dotenv import load_dotenv
from requests.exceptions import HTTPError, ConnectionError
from page_analyzer.validate import validate_url
from urllib.parse import urlparse

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
)

load_dotenv()

# Настройка логирования
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
DATABASE_URL = os.getenv('DATABASE_URL')


def get_connection():
    return psycopg2.connect(DATABASE_URL)


def get_content_of_page(page_data):
    soup = bs4.BeautifulSoup(page_data, 'html.parser')
    h1 = soup.find('h1').get_text() if soup.find('h1') else ''
    title = soup.find('title').get_text() if soup.find('title') else ''
    meta_tag = soup.find('meta', {"name": "description"})
    meta = meta_tag.attrs['content'] if meta_tag else ''
    return h1, title, meta


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/urls', methods=['POST'])
def post_url():
    url = request.form.get('url')
    parsed_url = urlparse(url)
    valid_url = f"{parsed_url.scheme}://{parsed_url.netloc}"

    errors = validate_url(valid_url)
    if errors:
        flash("Invalid URL", "alert alert-danger")
        return redirect(url_for('index'))

    # Проверка наличия URL в базе данных
    with get_connection() as conn:
        with conn.cursor(
            cursor_factory=psycopg2.extras.NamedTupleCursor
        ) as cur:
            cur.execute("SELECT id FROM urls WHERE name = %s", [valid_url])
            result = cur.fetchone()
            if result:
                flash("Page already exists", "alert alert-info")
                return redirect(url_for('url_added', id=result.id))

    # Проверка валидности URL
    try:
        response = requests.get(valid_url)
        response.raise_for_status()
        if not response.text:
            flash("Empty response from the URL", "alert alert-danger")
            return redirect(url_for('index'))
    except (HTTPError, ConnectionError) as e:
        logging.error(f"Error accessing URL {valid_url}: {e}")
        flash("Invalid URL or website is unreachable", "alert alert-danger")
        return redirect(url_for('index'))

    with get_connection() as conn:
        with conn.cursor() as cur:
            date = datetime.date.today()
            cur.execute(
                """
                INSERT INTO urls (name, created_at)
                VALUES (%s, %s) RETURNING id
                """, [valid_url, date]
            )
            url_id = cur.fetchone()[0]
            conn.commit()
        flash("Page successfully added", "alert alert-success")
        return redirect(url_for('url_added', id=url_id))


@app.route('/urls/<int:id>')
def url_added(id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT name, created_at
                FROM urls
                WHERE id = %s
                """, [id]
            )
            row = cur.fetchone()
            url_name = row.name if row else None
            url_created_at = row.created_at if row else None

    with get_connection() as conn:
        with conn.cursor(
            cursor_factory=psycopg2.extras.NamedTupleCursor
        ) as cur:
            cur.execute(
                """
                SELECT id, created_at, status_code, h1, title, description
                FROM url_checks
                WHERE url_id = %s
                ORDER BY id DESC
                """, [id]
            )
            rows = cur.fetchall()
    return render_template(
        'url.html',
        url_name=url_name,
        url_id=id,
        url_created_at=url_created_at,
        checks=rows
    )


@app.route('/urls', methods=['GET'])
def urls_get():
    with get_connection() as conn:
        with conn.cursor(
            cursor_factory=psycopg2.extras.NamedTupleCursor
        ) as cur:
            cur.execute(
                """
                SELECT
                    DISTINCT ON (urls.id)
                        urls.id,
                        urls.name,
                        MAX(url_checks.created_at) AS max,
                        url_checks.status_code
                FROM urls
                LEFT JOIN url_checks ON urls.id = url_checks.url_id
                GROUP BY urls.id, url_checks.status_code
                ORDER BY urls.id DESC
                """
            )
            rows = cur.fetchall()
    return render_template(
        'urls.html',
        urls=rows
    )


@app.route('/urls/<int:id>/checks', methods=['POST'])
def id_check(id):
    with get_connection() as conn:
        with conn.cursor(
            cursor_factory=psycopg2.extras.NamedTupleCursor
        ) as cur:
            cur.execute(
                """
                SELECT name
                FROM urls
                WHERE id = %s
                """, [id]
            )
            result = cur.fetchone()

    url_name = result.name if result else None
    try:
        response = requests.get(url_name)
        response.raise_for_status()
        h1, title, description = get_content_of_page(response.text)
        status_code = response.status_code

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO url_checks (
                        url_id, status_code, h1, title, description, created_at
                    )
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    [
                        id, status_code, h1, title, description,
                        datetime.datetime.now()
                    ]
                )
                conn.commit()
        flash("Check completed successfully", "alert alert-success")
    except Exception as e:
        logging.error(f"An error occurred during the check: {e}")
        flash(
            f"An error occurred during the check: {str(e)}",
            "alert alert-danger"
        )

    return redirect(url_for('url_added', id=id))


@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500
