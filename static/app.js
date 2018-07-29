const examples = Vue.component('Example', {
    template: '#example-template',
    delimiters: ['[[', ']]'],
    props: ['provider', 'url', 'examples', 'term'],
});

const messages = Vue.component('Messages', {
    template: '#messages-template',
    delimiters: ['[[', ']]'],
    props: ['messages'],
});

const searchForm = Vue.component('SearchForm', {
    template: '#search-form-template',
    delimiters: ['[[', ']]'],
    props: ['providers', 'query', 'isBusy'],
    data: function () {
        return {
            term: this.query,
        }
    },
    computed: {
        enabledProviders() {
            return this.providers.filter(p => p.enabled);
        },
        canSearch() {
            return !this.isBusy
                && this.term
                && this.enabledProviders.length > 0;
        }
    },
    watch: {
        query(now, then) {
            this.term = now;
        }
    },
    methods: {
        onSubmit() {
            this.$emit('search', this.term, this.enabledProviders)
        },
    },
});


const app = new Vue({
    el: '#app',
    delimiters: ['[[', ']]'],
    data: {
        providers: providers.map(name => ({name, enabled: true})),
        query: '',
        autoSearch: true,
        isBusy: false,
        examples: [],
        messages: [],
        timeout: null
    },
    computed: {
        hasMessages() {
            return this.messages.length > 0;
        },
        hasExamples() {
            return this.examples.filter(ex => ex.examples.length).length > 0;
        },
        enabledProviders() {
            return this.providers.filter(p => p.enabled);
        },
    },
    methods: {
        onSearch(term, providers) {
            this.search(term, providers)
        },
        search: function (term, providers) {
            if (!term) return;
            if (!providers) return;

            this.examples = [];
            this.messages = [];

            this.isBusy = true;
            Promise.all(
                providers.map(p => this.fetchExamples(p.name, term)
                    .then(response => {
                        if (response.status !== 'success') {
                            throw new Error(response.message);
                        }
                        this.processExamples(response.data);
                    })
                    .catch(error => {
                        this.processError(p.name, error.message);
                    }))
            )
                .then(() => this.isBusy = false);


        },
        fetchExamples(provider, term) {
            return fetch(`/examples/${provider}/${term}`)
                .then(res => res.json());
        },
        processExamples(data) {
            this.examples.unshift(data);
        },
        processError(provider, message) {
            this.messages.push({provider, message});

            if (this.timeout) clearTimeout(this.timeout);
            this.timeout = setTimeout(() => this.messages = [], 5000);
        },
        flattenExamples() {
            return this.examples
                .filter(ex => ex.examples.length)
                .reduce((carry, ex) => carry.concat(ex.examples), [])
                .join('\n')
                .trim();
        },
        copyExamples() {
            this.copyTextToClipboard(this.flattenExamples());
        },
        copyTextToClipboard(text) {
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
        bindKeyboard() {
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
        bindPaste() {
            document.addEventListener('paste', function (e) {
                this.query = (e.clipboardData || window.clipboardData).getData('text').trim();
                if (this.autoSearch) {
                    this.search(this.query, this.enabledProviders);
                }
            }.bind(this));
        }
    },
    created() {
        this.bindKeyboard();
        this.bindPaste();
    },
    mounted() {
        document.querySelector('[name=query]').focus();
    }
});