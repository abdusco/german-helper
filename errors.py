class NoExamples(Exception):
    def __str__(self):
        return 'No examples provided'


class MissingContent(Exception):
    description = 'Expected content missing on the page'

    def __init__(self, description=None):
        if not description:
            self.description = description

    def __str__(self):
        return self.description
