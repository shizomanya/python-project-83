import re
import logging
import requests
from bs4 import BeautifulSoup


def try_get_url(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as error:
        logging.exception(error)
        return None


def get_status_code(response):
    return response.status_code


def get_url_seo_data(response_text):
    soup = BeautifulSoup(response_text, 'html.parser')
    h1 = soup.h1.string if soup.h1 else ''
    title = soup.title.string if soup.title else ''
    description_tag = soup.find('meta', attrs={"name": "description"})
    description = ''
    if description_tag:
        content = description_tag.get('content', '')
        pattern = r'"(.+?)"'
        match = re.search(pattern, content)
        if match:
            description = match.group(1)
        else:
            description = content

    return h1, title, description
