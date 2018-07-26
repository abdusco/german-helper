from requests import get, Response
from parsers import WiktionaryDeutschParser, DudenParser, LingueeParser
from urllib.parse import urlencode, quote


def make_wiktionary_url(term: str, endpoint='https://de.wiktionary.org/wiki/'):
    return ''.join((endpoint, quote(term)))


def make_duden_url(term: str, endpoint='https://www.duden.de/rechtschreibung/'):
    return ''.join((endpoint, quote(term)))


def make_linguee_url(term: str, endpoint='https://www.linguee.com/english-german/search?'):
    return ''.join((endpoint, urlencode({
        'query': term
    })))


def get_html(url: str):
    response: Response = get(url)
    if response.status_code != 200:
        raise ReferenceError('Term not found')
    return response.content


def get_wiktionary_examples(term):
    try:
        url = make_wiktionary_url(term)
        wikt = WiktionaryDeutschParser(get_html(url))
        return wikt.examples
    except:
        return []


def get_duden_examples(term):
    try:
        url = make_duden_url(term)
        duden = DudenParser(get_html(url))
        return duden.examples
    except:
        return []


def get_linguee_examples(term):
    try:
        url = make_linguee_url(term)
        linguee = LingueeParser(get_html(url))
        return linguee.examples
    except:
        return []
