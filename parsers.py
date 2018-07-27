from bs4 import BeautifulSoup, Tag
import re


class WiktionaryDeutschParser:
    name = 'Wiktionary Deutsch'

    def __init__(self, html: str):
        self.page = BeautifulSoup(html, 'html.parser')

    @property
    def term(self):
        title = self.page.find('h1')
        return title.text

    @property
    def examples(self):
        try:
            examples_title: Tag = self.page.find(title='Verwendungsbeispielsätze')
            example_list = examples_title.find_next_siblings('dl')[0]
            examples = example_list.text.split('\n')
            return self.__clean_examples(examples)
        except:
            return []

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
        return title.text

    @property
    def examples(self):
        try:
            example_title = self.page.find('h3', string=re.compile('Beispiel'))
            example_section = example_title.find_parent('section', class_='block')
            example_titles = example_section.find_all('h3', text=re.compile('Beispiel'))
            example_wrappers = [t.next_sibling for t in example_titles if t.next_siblings]
            w: Tag
            examples = []
            for w in example_wrappers:
                try:
                    if w.name == 'ul':
                        examples += [li.text.strip() for li in w.find_all('li')]
                    else:
                        examples += [w.text.strip()]
                except:
                    pass

            return examples
        except:
            return []


class LingueeParser:
    name = 'Linguee'

    def __init__(self, html: str):
        self.page = BeautifulSoup(html, 'html.parser')

    @property
    def term(self):
        featured_lemma = self.page.select_one('.lemma.featured .dictLink')
        return featured_lemma.text

    @property
    def examples(self):
        try:
            examples = self.page.select('.exact .example')
            examples = [e.text.replace(' — ', '\n').strip()
                        for e in examples]
            return examples
        except:
            return []
