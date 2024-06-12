import os
import logging
import requests
import psycopg2
import psycopg2.extras
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from dotenv import load_dotenv
from page_analyzer.validate import validate_url
from flask import Flask, request, flash, redirect, render_template, url_for
from requests.exceptions import HTTPError, ConnectionError, Timeout

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
DATABASE_URL = os.getenv('DATABASE_URL')


def get_connection():
    return psycopg2.connect(DATABASE_URL)


def get_content_of_page(page_data):
    soup = BeautifulSoup(page_data, 'html.parser')
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

    try:
        with get_connection() as conn:
            with conn.cursor(
                cursor_factory=psycopg2.extras.NamedTupleCursor
            ) as cur:
                cur.execute(
                    "SELECT id FROM urls WHERE name = %s", [valid_url]
                )
                result = cur.fetchone()
                if result:
                    flash("Page already exists", "alert alert-info")
                    return redirect(url_for('url_added', id=result.id))

                cur.execute(
                    """
                    INSERT INTO urls (name, created_at)
                    VALUES (%s, CURRENT_DATE) RETURNING id
                    """,
                    [valid_url]
                )
                url_id = cur.fetchone().id
                conn.commit()
                flash("URL successfully added", "alert alert-success")
                return redirect(url_for('url_added', id=url_id))
    except Exception as e:
        logging.error(f"Database error: {e}")
        flash("An error occurred while adding the URL", "alert alert-danger")

    return redirect(url_for('index'))


@app.route('/urls/<int:id>')
def url_added(id):
    try:
        with get_connection() as conn:
            with conn.cursor(
                cursor_factory=psycopg2.extras.NamedTupleCursor
            ) as cur:
                cur.execute(
                    "SELECT name, created_at FROM urls WHERE id = %s", [id]
                )
                row = cur.fetchone()
                if row:
                    url_name, url_created_at = row.name, row.created_at
                else:
                    flash("URL not found", "alert alert-danger")
                    return redirect(url_for('index'))

                cur.execute(
                    """
                    SELECT id, created_at, status_code, h1, title, description
                    FROM url_checks
                    WHERE url_id = %s
                    ORDER BY id DESC
                    """,
                    [id]
                )
                checks = cur.fetchall()
                return render_template(
                    'url.html',
                    url_name=url_name,
                    url_id=id,
                    url_created_at=url_created_at,
                    checks=checks
                )
    except Exception as e:
        logging.error(f"Database error: {e}")
        flash(
            "An error occurred while fetching URL data",
            "alert alert-danger"
            )

    return redirect(url_for('index'))


@app.route('/urls', methods=['GET'])
def urls_get():
    try:
        with get_connection() as conn:
            with conn.cursor(
                cursor_factory=psycopg2.extras.NamedTupleCursor
            ) as cur:
                cur.execute(
                    """
                    SELECT DISTINCT ON (urls.id) urls.id, urls.name,
                    MAX(url_checks.created_at) AS last_check,
                    url_checks.status_code
                    FROM urls
                    LEFT JOIN url_checks ON urls.id = url_checks.url_id
                    GROUP BY urls.id, url_checks.status_code
                    ORDER BY urls.id DESC
                    """
                )
                urls = cur.fetchall()
                return render_template('urls.html', urls=urls)
    except Exception as e:
        logging.error(f"Database error: {e}")
        flash("An error occurred while fetching URLs", "alert alert-danger")

    return redirect(url_for('index'))


@app.route('/urls/<int:id>/checks', methods=['POST'])
def id_check(id):
    try:
        with get_connection() as conn:
            with conn.cursor(
                cursor_factory=psycopg2.extras.NamedTupleCursor
            ) as cur:
                cur.execute("SELECT name FROM urls WHERE id = %s", [id])
                result = cur.fetchone()
                if not result:
                    flash("URL not found", "alert alert-danger")
                    return redirect(url_for('index'))

                url_name = result.name

                response = requests.get(url_name, timeout=5)
                response.raise_for_status()
                h1, title, description = get_content_of_page(response.text)
                status_code = response.status_code

                cur.execute(
                    """
                    INSERT INTO url_checks (
                        url_id, status_code, h1, title, description, created_at
                    )
                    VALUES (%s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
                    """,
                    [id, status_code, h1, title, description]
                )
                conn.commit()
                flash("Check completed successfully", "alert alert-success")
    except (HTTPError, ConnectionError, Timeout) as e:
        logging.error(f"Error checking URL {id}: {e}")
        flash("Error checking the URL", "alert alert-danger")
    except Exception as e:
        logging.error(f"Database error: {e}")
        flash("An error occurred while checking the URL", "alert alert-danger")

    return redirect(url_for('url_added', id=id))


@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500


if __name__ == '__main__':
    app.run(debug=True)
