from werkzeug.exceptions import NotFound


class NoExamples(Exception):
    def __str__(self):
        return 'No examples provided'


class MissingContent(NotFound):
    def __init__(self, missing: str):
        self.missing = missing

    def __str__(self):
        return f'Expected content "{self.missing}" missing on the page'
