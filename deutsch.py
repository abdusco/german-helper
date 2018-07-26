from flask import Flask, render_template, abort, redirect, request, url_for, jsonify
import providers

app = Flask(__name__)


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/examples/<provider>/<term>')
def examples_json(provider, term):
    term = term.strip()
    if provider == 'wiktionary':
        examples = providers.get_wiktionary_examples(term)
    elif provider == 'duden':
        examples = providers.get_duden_examples(term)
    elif provider == 'linguee':
        examples = providers.get_linguee_examples(term)

    if not examples:
        return abort(404)

    return jsonify({
        'term': term,
        'provider': provider,
        'examples': examples
    })


if __name__ == '__main__':
    app.run(debug=True)
