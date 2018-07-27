const exampleProvider = Vue.component('example', {
    template: '#provider-example',
    delimiters: ['[[', ']]'],
    props: ['data'],
    methods: {
        breakLines: function (lines) {
            return lines.map(l => l.replace('\n', '<br>'));
        }
    }
});

const app = new Vue({
    el: '#app',
    delimiters: ['[[', ']]'],
    data: {
        providers: providers.map(p => ({name: p, active: true})),
        query: '',
        examples: [],
    },
    methods: {
        canSearch: function () {
            return this.providers.filter(p => p.active).length > 0;
        },
        hasExamples: function () {
            return this.examples
                .filter(ex => ex.examples.length)
                .length > 0;
        },
        onSubmit: function () {
            this.search();
        },
        search: function () {
            this.examples = [];
            let activeProviders = this.providers.filter(p => p.active);
            activeProviders.forEach(p => {
                this.fetchExamples(p.name, this.query)
                    .then(data => {
                        this.examples.push(data)
                    })
                    .catch(err => {
                        this.examples.push({
                            provider: p.name,
                            term: 'Error',
                            examples: [],
                            url: ''
                        })
                    })
            });
        },
        fetchExamples: function (provider, term) {
            return fetch(`/examples/${provider}/${term}`)
                .then(res => res.json())
        },
        copyExamples: function () {
            let all = this.examples
                .map(ex => ex.examples.join('\n'))
                .join('\n')
                .trim();
            this.copyTextToClipboard(all);
        },
        copyTextToClipboard: function (text) {
            if (window.clipboardData && window.clipboardData.setData) {
                // IE specific code path to prevent textarea being shown while dialog is visible.
                return clipboardData.setData("Text", text);
            } else if (document.queryCommandSupported && document.queryCommandSupported("copy")) {
                var textarea = document.createElement("textarea");
                textarea.textContent = text;
                textarea.style.position = "fixed";  // Prevent scrolling to bottom of page in MS Edge.
                document.body.appendChild(textarea);
                textarea.select();
                try {
                    return document.execCommand("copy");  // Security exception may be thrown by some browsers.
                } catch (ex) {
                    console.warn("Copy to clipboard failed.", ex);
                    return false;
                } finally {
                    document.body.removeChild(textarea);
                }
            }
        },
        bindKeyboard: function () {
            window.addEventListener('keydown', function (e) {
                if (e.altKey && e.key === 'c') {
                    this.copyExamples();
                }
            }.bind(this));
        },
        bindPaste: function () {
            window.addEventListener('paste', function (e) {
                this.query = (e.clipboardData || window.clipboardData).getData('text').trim();
                this.search();
            }.bind(this));
        }
    },
    created: function () {
        this.bindKeyboard();
        this.bindPaste();
    }
});