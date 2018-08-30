from parsers import *
from urllib.parse import quote
from slugify import slugify_de
from bs4 import BeautifulSoup
from werkzeug.exceptions import NotFound, ServiceUnavailable
from requests import get, Response
import re


def get_providers_list():
    return [
        'linguee',
        'duden',
        'wiktionary',
        'verbformen',
        'reverso',
        'collins',
    ]


def get_html(url: str, headers=None):
    if not headers:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3496.0 Safari/537.36'
        }
    response: Response = get(url, headers=headers)
    if 400 <= response.status_code < 500:
        raise NotFound
    elif 500 <= response.status_code:
        raise ServiceUnavailable
    return response.content


def get_wiktionary(term):
    url = f'https://de.wiktionary.org/wiki/{quote(term)}'

    return WiktionaryDeutschParser(get_html(url)), url


def get_duden(term):
    url = f'https://www.duden.de/rechtschreibung/{slugify_de(term)}'
    search_url = f'https://www.duden.de/suchen/dudenonline/{quote(term)}'

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


def get_verbformen(term: str):
    if not term.endswith('n'):
        raise NotFound('Not a verb')
    url = f'https://www.verbformen.com/conjugation/examples/{quote(term)}.htm'

    return VerbFormenParser(get_html(url)), url


def get_verbformen_conjugation(term: str):
    if not term.endswith('n'):
        raise NotFound('Not a verb')
    url = f'https://www.verbformen.de/konjugation/?w={quote(term)}'

    return VerbFormenConjugationParser(get_html(url)), url


def get_reverso(term: str):
    url = f'http://context.reverso.net/translation/german-english/{quote(term)}'
    html = get_html(url)

    return ReversoContextParser(html), url


def get_collins(term: str):
    url = f'https://www.collinsdictionary.com/de/worterbuch/deutsch-englisch/{quote(term)}'
    html = get_html(url)

    return CollinsParser(html), url
