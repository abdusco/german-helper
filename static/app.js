const examples = Vue.component('example', {
    template: '#example-template',
    delimiters: ['[[', ']]'],
    props: ['provider', 'url', 'examples', 'term'],
});

const messages = Vue.component('messages', {
    template: '#messages-template',
    delimiters: ['[[', ']]'],
    props: ['messages'],
});

const app = new Vue({
    el: '#app',
    delimiters: ['[[', ']]'],
    data: {
        providers: providers.map(p => ({
            name: p,
            enabled: true
        })),
        query: '',
        examples: [],
        messages: [],
    },
    methods: {
        hasMessages: function () {
            return this.messages.length > 0;
        },
        canSearch: function () {
            return this.providers
                .filter(p => p.enabled)
                .length > 0;
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
            this.messages = [];

            this.providers
                .filter(p => p.enabled)
                .forEach(p => {
                    this.fetchExamples(p.name, this.query)
                        .then(response => {
                            if (response.status !== 'success') {
                                throw new Error(response.message);
                            }
                            this.processExamples(response.data);
                        })
                        .catch(error => {
                            this.processError(p.name, error.message);
                        });
                });
        },
        fetchExamples: function (provider, term) {
            return fetch(`/examples/${provider}/${term}`)
                .then(res => res.json());
        },
        processExamples: function (data) {
            this.examples.unshift(data);
        },
        processError: function (provider, message) {
            this.messages.push({provider, message});
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
                    if (!this.hasExamples()) return;
                    this.$el.click();
                    this.copyExamples();
                }
                else if (e.altKey && e.key === 'n') {
                    this.$el.classList.toggle('night');
                }
            }.bind(this));
        },
        bindPaste: function () {
            document.addEventListener('paste', function (e) {
                this.query = (e.clipboardData || window.clipboardData).getData('text').trim();
                this.search();
            }.bind(this));
        }
    },
    created: function () {
        this.bindKeyboard();
        this.bindPaste();
    },
    mounted: function () {
        document.querySelector('[name=q]').focus();
    }
});