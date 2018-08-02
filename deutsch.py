from flask import Flask, render_template, abort, redirect, request, url_for, jsonify
import providers
from werkzeug.exceptions import NotFound, ServiceUnavailable, BadRequest
from errors import NoExamples, MissingContent

app = Flask(__name__)


def get_providers_list():
    return ['linguee', 'duden', 'wiktionary', 'verbformen']


@app.route('/')
def home():
    return render_template('home.html', providers=get_providers_list())


@app.route('/examples/<provider_name>/<term>')
def examples_json(provider_name, term):
    try:
        term = term.strip()
        if provider_name == 'wiktionary':
            provider, url = providers.get_wiktionary(term)
        elif provider_name == 'duden':
            provider, url = providers.get_duden(term)
        elif provider_name == 'linguee':
            provider, url = providers.get_linguee(term)
        elif provider_name == 'verbformen':
            provider, url = providers.get_verbformen(term)

        return jsonify(status='success', data={
            'term': provider.term,
            'url': url,
            'provider': provider.name,
            'examples': provider.examples
        })
    except NoExamples as e:
        raise e
    except NotFound:
        raise NotFound(f'No relevant results for „{term}“')


@app.route('/conjugation/<verb>')
def declension(verb: str):
    provider, url = providers.get_verbformen_conjugation(verb)
    return jsonify(status='success', data={
        'conjugation': provider.conjugation,
        'conjugation_str': ', '.join(provider.conjugation),
        'provider': provider.name
    })


@app.errorhandler(ServiceUnavailable)
def handle_service_error(error):
    return jsonify(status='fail', message=str(error)), 503


@app.errorhandler(NoExamples)
@app.errorhandler(NotFound)
@app.errorhandler(MissingContent)
def handle_not_found_error(error):
    return jsonify(status='fail', message=str(error) or error.description), 404


if __name__ == '__main__':
    app.run(debug=True)
