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


def get_status_code(response):
    return response.status_code


def get_url_seo_data(response):
    soup = BeautifulSoup(response.text, 'html.parser')
    if soup.h1:
        h1 = soup.h1.string
    else:
        h1 = ''
    if soup.title:
        title = soup.title.string
    else:
        title = ''
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
