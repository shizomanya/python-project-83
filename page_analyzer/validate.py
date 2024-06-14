import validators
from urllib.parse import urlparse

MAX_URL_LEN = 255


def check_url_len(url):
    return len(url) > MAX_URL_LEN


def validate_url(url):
    return not validators.url(url)


def normalize_url(url):
    url_parts = urlparse(url)
    return f"{url_parts.scheme}://{url_parts.netloc}"
