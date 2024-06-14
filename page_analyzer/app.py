import os
from datetime import date
from dotenv import load_dotenv
from psycopg2.extras import DictCursor
from psycopg2 import connect, OperationalError
from flask import (
    Flask, request, render_template, redirect, url_for, flash,
    get_flashed_messages
)
from .parser import get_url_seo_data, try_get_url, get_status_code
from .validate import validate_url, check_url_len, normalize_url

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


def connect_db(func):
    def wrapper(*args, **kwargs):
        try:
            conn = connect(DATABASE_URL)
            cur = conn.cursor(cursor_factory=DictCursor)
        except OperationalError:
            print("Unable to establish connection to database")
            return None
        result = func(cur, *args, **kwargs)
        conn.commit()
        conn.close()
        cur.close()
        return result
    return wrapper


@connect_db
def get_all_urls(cur):
    cur.execute("SELECT * FROM urls ORDER BY id DESC")
    return cur.fetchall()


@connect_db
def get_url_data(cur, id):
    cur.execute(
        "SELECT id, name, created_at, last_check, status_code "
        "FROM urls WHERE id = %s",
        (id,)
    )
    url_data = cur.fetchone()
    return url_data


@connect_db
def get_url_checks(cur, url_id):
    cur.execute(
        "SELECT * FROM url_checks WHERE url_id = (%s) ORDER BY id DESC",
        (url_id,)
    )
    return cur.fetchall()


@connect_db
def get_url_by_name(cur, url):
    cur.execute("SELECT * FROM urls WHERE name = (%s)", (url,))
    return cur.fetchone()


@connect_db
def add_url(cur, url, created_at):
    last_check = date.today()
    cur.execute(
        "INSERT INTO urls (name, created_at, last_check) "
        "VALUES (%s, %s, %s) RETURNING id",
        (url, created_at, last_check)
    )
    return cur.fetchone()


@connect_db
def add_url_check(cur, id, status_code, h1, title, description, created_at):
    url_data = get_url_data(id)
    if url_data is None:
        return None

    h1 = h1 if h1 is not None else ''

    cur.execute("""
        INSERT INTO url_checks (url_id, status_code, h1, title,
                        description, created_at)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (id, status_code, h1, title, description, created_at))

    cur.execute("""
        UPDATE urls
        SET last_check = %s, status_code = %s
        WHERE id = %s
    """, (created_at, status_code, id))

    return True


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/urls', methods=['GET'])
def urls_get():
    urls = get_all_urls()
    return render_template('urls.html', urls=urls)


@app.route('/urls', methods=['POST'])
def post_url():
    input_url = request.form.get('url')
    if check_url_len(input_url):
        flash('URL exceeds 255 characters', 'alert alert-danger')
        return render_template('index.html'), 422
    if validate_url(input_url):
        flash('Invalid URL', 'alert alert-danger')
        return render_template('index.html'), 422

    url = normalize_url(input_url)
    url_data = get_url_by_name(url)
    if url_data:
        flash('Page already exists', "alert alert-info")
    else:
        created_at = date.today()
        url_data = add_url(url, created_at)
        flash('Page successfully added', 'alert alert-success')
    url_id = url_data['id']
    return redirect(url_for('url_added', id=url_id))


@app.route('/urls/<int:id>')
def url_added(id):
    messages = get_flashed_messages(with_categories=True)
    url_data = get_url_data(id)
    if not url_data:
        flash("URL not found", "alert alert-danger")
        return redirect(url_for('index'))

    checks = get_url_checks(id)
    return render_template(
        'url.html',
        messages=messages,
        url_name=url_data['name'],
        url_id=id,
        url_created_at=url_data['created_at'],
        checks=checks
    )


@app.route('/urls/<int:id>/checks', methods=['POST'])
def id_check(id):
    url_data = get_url_data(id)
    if not url_data:
        flash("URL not found", "alert alert-danger")
        return redirect(url_for('index'))

    url = url_data['name']
    response = try_get_url(url)
    if response:
        flash("Check completed successfully", "alert alert-success")
        check_created_at = date.today()
        h1, title, description = get_url_seo_data(response)
        status_code = get_status_code(response)
        if status_code == 200:
            add_url_check(
                id, status_code, h1, title, description, check_created_at
            )
    else:
        flash("Error checking the URL", "alert alert-danger")
    return redirect(url_for('url_added', id=id))


@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500


if __name__ == '__main__':
    app.run(debug=True)
