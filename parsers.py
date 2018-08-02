from bs4 import BeautifulSoup, Tag
from werkzeug.exceptions import NotFound, ServiceUnavailable
from errors import NoExamples, MissingContent
import re


class WiktionaryDeutschParser:
    name = 'Wiktionary Deutsch'

    def __init__(self, html: str):
        self.page = BeautifulSoup(html, 'html.parser')

    @property
    def term(self):
        title = self.page.find('h1')
        if title:
            return title.text
        raise MissingContent('No term on the page')

    @property
    def examples(self):
        try:
            examples_title: Tag = self.page.find(title='Verwendungsbeispielsätze')
            example_list = examples_title.find_next_siblings('dl')[0]
            examples = example_list.text.split('\n')
            return self.__clean_examples(examples)
        except:
            raise NoExamples

    def __clean_examples(self, examples: list):
        # remove [x] from examples
        no_brackets = [re.sub('\[[^\]]+\]', '', e) for e in examples]
        return [e.strip() for e in no_brackets if e]


class DudenParser:
    name = 'Duden.de'

    def __init__(self, html: str):
        self.page = BeautifulSoup(html, 'html.parser')

    @property
    def term(self):
        title = self.page.find('h1')
        lexem = self.page.select_one('.entry .lexem')
        if not title or not lexem:
            raise MissingContent('No term on the page')
        return f'{title.text} ({lexem.text})'

    @property
    def examples(self):
        try:
            example_title = self.page.find('h3', string=re.compile('Beispiel'))
            example_section = example_title.find_parent('section', class_='block')
            example_titles = example_section.find_all('h3',
                                                      text=re.compile('(Beispiel|Wendungen|Redensarten|Sprichwörter)'))
            example_wrappers = [t.next_sibling for t in example_titles if t.next_siblings]
        except:
            raise NoExamples

        examples = []
        for w in example_wrappers:
            examples += self.__extract_examples_from_tag(w)
        return examples

    def __extract_examples_from_tag(self, w: Tag):
        try:
            if w.name == 'ul':
                return [li.text.strip() for li in w.find_all('li')]
            else:
                return [w.text.strip()]
        except:
            return []


class LingueeParser:
    name = 'Linguee'

    def __init__(self, html: str):
        self.page = BeautifulSoup(html, 'html.parser')

    @property
    def term(self):
        featured_lemma = self.page.select_one('.lemma.featured .dictLink')
        lemma_type = self.page.select_one('.lemma.featured .tag_wordtype')

        if not featured_lemma or not lemma_type:
            raise MissingContent('No term on the page')

        return f'{featured_lemma.text} ({lemma_type.text})'

    @property
    def examples(self):
        try:
            examples = self.page.select('.isMainTerm .exact .example')
            examples = [e.text.replace(' — ', '\n').strip()
                        for e in examples]
            if not examples:
                raise NoExamples
            return examples
        except:
            raise NoExamples


class VerbFormenParser:
    name = 'VerbFormen'

    def __init__(self, html: str):
        self.page = BeautifulSoup(html, 'html.parser')

    @property
    def term(self):
        title = self.page.find('h1')
        return title.text

    @property
    def examples(self):
        examples = self.page.select('.rLst')
        examples_text = [ex.text for ex in examples]
        # unicode sequence is for superscript digits for footnotes
        examples_text = [re.sub('(^\W+|\W+$|[\u2070\u00b9\u00b2\u00b3\u2074\u2075\u2076\u2077\u2078\u2079])', '', ex)
                         for ex in examples_text]
        return examples_text
