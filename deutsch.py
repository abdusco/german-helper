from flask import Flask, render_template, abort, redirect, request, url_for, jsonify
import providers
from werkzeug.exceptions import NotFound, ServiceUnavailable, BadRequest
from errors import NoExamples, MissingContent
import deepl

app = Flask(__name__)


@app.route('/')
def home():
    return render_template('home.html', providers=providers.get_providers_list())


@app.route('/examples/<provider_name>/<term>')
def examples_json(provider_name, term):
    try:
        term = term.strip()
        assert term
        provider_name = provider_name.strip()
        for p in providers.get_providers_list():
            if provider_name == p:
                provider, url = getattr(providers, f'get_{p}')(term)
                break

        return jsonify(status='success', data={
            'term': provider.term,
            'url': url,
            'provider': provider.name,
            'examples': provider.examples
        })
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


@app.route('/translate/<phrase>')
def translate(phrase: str):
    phrase = phrase.strip()
    assert phrase

    translations = deepl.get_translations(phrase)
    return jsonify(status='success', data=translations)


@app.errorhandler(AssertionError)
def handle_validation_error(error):
    return jsonify(status='fail', message=str(error)), 400


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
