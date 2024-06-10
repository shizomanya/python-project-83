import os
import sys
import validators

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
)


def validate_url(url):
    errors = []
    if len(url) > 255:
        errors.append('URL exceeds 255 characters')
    elif not url:
        errors.append("URL is required")
    elif not validators.url(url):
        errors.append('Invalid URL')

    return errors
