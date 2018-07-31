const example = Vue.component('Example', {
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
    props: ['providers', 'query', 'isBusy', 'autoSearch'],
    data() {
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
        focusSearch() {
            let input = document.querySelector('[name=query]');
            input.focus();
            input.select();
        },
        bindKeyboard() {
            window.addEventListener('keydown', function (e) {
                if (e.key === 'Escape') {
                    this.focusSearch();
                }
            }.bind(this))
        },
        bindPaste() {
            document.addEventListener('paste', function (e) {
                this.term = (e.clipboardData || window.clipboardData).getData('text').trim();
                if (this.autoSearch && this.canSearch) {
                    this.$emit('search', this.term, this.enabledProviders);
                }
            }.bind(this));
        },
    },
    mounted() {
        this.bindKeyboard();
        this.bindPaste();
        this.focusSearch();
    }
});

const examples = Vue.component('Examples', {
    template: '#examples-template',
    delimiters: ['[[', ']]'],
    props: ['examples'],
    data() {
        return {
            availableExamples: this.examples.map(e => ({
                picked: e.examples.length > 0,
                ...e
            }))
        }
    },
    watch: {
        examples(now, then) {
            this.availableExamples = now.map(e => ({
                picked: e.examples.length > 0,
                ...e
            }))
        }
    },
    computed: {
        pickedExamples() {
            return this.availableExamples.filter(ex => ex.picked)
        },
    },
    methods: {
        flattenExamples() {
            return this.pickedExamples
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
        onKeyDown(e) {
            if (e.altKey && e.key === 'c') {
                if (!this.pickedExamples.length) return;
                this.copyExamples();
            }
        }

    },
    mounted() {
        window.addEventListener('keydown', this.onKeyDown);
    },
    beforeDestroy() {
        window.removeEventListener('keydown', this.onKeyDown);
    }
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
        bindKeyboard() {
            window.addEventListener('keydown', function (e) {
                if (e.altKey && e.key === 'n') {
                    this.$el.classList.toggle('night');
                }
            }.bind(this));
        },
    },
    created() {
        this.bindKeyboard();
    },
});