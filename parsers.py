from bs4 import BeautifulSoup, Tag
import re


class WiktionaryDeutschParser:
    def __init__(self, html: str):
        self.page = BeautifulSoup(html, 'html.parser')

    @property
    def examples(self):
        examples_title: Tag = self.page.find(title='Verwendungsbeispielsätze')
        example_list = examples_title.find_next_siblings('dl')[0]
        examples = example_list.text.split('\n')
        return self.__clean_examples(examples)

    def __clean_examples(self, examples: list):
        # remove [x] from examples
        no_brackets = [re.sub('\[[^\]]+\]', '', e) for e in examples]
        return [e.strip() for e in no_brackets if e]


class DudenParser:
    def __init__(self, html: str):
        self.page = BeautifulSoup(html, 'html.parser')

    @property
    def examples(self):
        example_title = self.page.find('h3', string=re.compile('Beispiel'))
        example_section = example_title.find_parent('section', class_='block')
        example_titles = example_section.find_all('h3', text=re.compile('Beispiel'))
        example_wrappers = [t.next_sibling for t in example_titles if t.next_siblings]
        w: Tag
        examples = []
        for w in example_wrappers:
            try:
                if w.name == 'ul':
                    examples += [li.text for li in w.find_all('li')]
                else:
                    examples += [w.text]
            except:
                pass

        return examples


class LingueeParser:
    def __init__(self, html: str):
        self.page = BeautifulSoup(html, 'html.parser')

    @property
    def examples(self):
        exact_translations = self.page.find(class_='exact')
        examples = exact_translations.find_all(class_='example')
        examples = [e.text.replace(' — ', '\n')
                    for e in examples]
        return examples
