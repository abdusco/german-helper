from requests import get, Response, RequestException
from parsers import WiktionaryDeutschParser, DudenParser, LingueeParser
from urllib.parse import quote
from slugify import slugify_de
from bs4 import BeautifulSoup
from werkzeug.exceptions import NotFound, ServiceUnavailable
import re


def get_html(url: str):
    response: Response = get(url)
    if 400 <= response.status_code < 500:
        raise NotFound
    elif 500 <= response.status_code:
        raise ServiceUnavailable
    return response.content


def get_wiktionary(term):
    url = f'https://de.wiktionary.org/wiki/{quote(term)}'
    return WiktionaryDeutschParser(get_html(url)), url


def get_duden(term):
    term_ascii = slugify_de(term)
    url = f'https://www.duden.de/rechtschreibung/{term_ascii}'
    search_url = f'https://www.duden.de/suchen/dudenonline/{term}'

    try:
        html = get_html(url)
    except NotFound:
        html = get_html(search_url)
        search_page = BeautifulSoup(html, 'html.parser')
        first_link = search_page.find('a', href=re.compile('rechtschreibung'))
        if not first_link:
            raise NotFound
        url = first_link.attrs['href']
        html = get_html(url)

    return DudenParser(html), url


def get_linguee(term):
    url = f'https://www.linguee.de/deutsch-englisch/uebersetzung/{quote(term)}.html'

    html = get_html(url)
    page = BeautifulSoup(html, 'html.parser')
    main_term = page.select_one('.isMainTerm')
    if not main_term:
        raise NotFound
    return LingueeParser(html), url
