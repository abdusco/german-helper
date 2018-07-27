from flask import Flask, render_template, abort, redirect, request, url_for, jsonify
import providers

app = Flask(__name__)


def get_providers_list():
    return ['linguee', 'duden', 'wiktionary']


@app.route('/')
def home():
    return render_template('home.html', providers=get_providers_list())


@app.route('/examples/<provider_name>/<term>')
def examples_json(provider_name, term):
    term = term.strip()
    if provider_name == 'wiktionary':
        provider, url = providers.get_wiktionary(term)
    elif provider_name == 'duden':
        provider, url = providers.get_duden(term)
    elif provider_name == 'linguee':
        provider, url = providers.get_linguee(term)

    if not provider:
        return abort(404)

    return jsonify({
        'term': provider.term,
        'url': url,
        'provider': provider.name,
        'examples': provider.examples
    })


if __name__ == '__main__':
    app.run(debug=True)
