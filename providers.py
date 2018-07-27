from requests import get, Response, RequestException
from parsers import WiktionaryDeutschParser, DudenParser, LingueeParser
from urllib.parse import quote
from slugify import slugify_de
from bs4 import BeautifulSoup
import re


def get_html(url: str):
    response: Response = get(url)
    if response.status_code != 200:
        raise FileNotFoundError('Page not found')
    return response.content


def get_wiktionary(term):
    try:
        url = f'https://de.wiktionary.org/wiki/{quote(term)}'
        return WiktionaryDeutschParser(get_html(url)), url
    except:
        return None, url


def get_duden(term):
    term_ascii = slugify_de(term)
    url = f'https://www.duden.de/rechtschreibung/{term_ascii}'
    search_url = f'https://www.duden.de/suchen/dudenonline/{term}'

    try:
        html = get_html(url)
    except FileNotFoundError:
        html = get_html(search_url)
        search_page = BeautifulSoup(html)
        url = search_page.find('a', href=re.compile('rechtschreibung')).attrs['href']
        html = get_html(url)
    except:
        return None, url

    return DudenParser(html), url


def get_linguee(term):
    try:
        url = f'https://www.linguee.com/english-german/search?query={term}'
        return LingueeParser(get_html(url)), url
    except:
        return None, url
