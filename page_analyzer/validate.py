import validators


def validate_url(url):
    errors = []
    if len(url) > 255:
        errors.append('URL exceeds 255 characters')
    elif not url:
        errors.append("URL is required")
    elif not validators.url(url):
        errors.append('Invalid URL')

    return errors
