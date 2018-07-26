(function (global) {

    function $(selector, context) {
        return (context || document).querySelector(selector)
    }

    function make(type) {
        return document.createElement(type);
    }

    function init() {
        let searchForm = $('.search');
        let searchInput = $('[name=q]', searchForm);
        let examplesContainer = $('.examples');

        searchForm.addEventListener('submit', handleSubmit);
        window.addEventListener('keydown', handleKeydown);

        function handleSubmit(e) {
            e.preventDefault();

            let term = searchInput.value;
            if (!term) return;

            examplesContainer.innerText = '';
            fetchExamples(term, providerResponded);
        }

        function providerResponded(data) {
            let section = makeProviderSection(data.provider, data.examples);
            examplesContainer.appendChild(section)
        }

        function handleKeydown(e) {
            if (e.key === 'Escape') {
                searchInput.focus();
                searchInput.select();
            }
        }
    }


    function fetchExamples(term, callback) {
        ['duden', 'wiktionary'].forEach(provider => {
            fetch(`/examples/${provider}/${term}`)
                .then(res => res.json())
                .then(callback)
                .catch(console.log)
        });
    }

    function makeProviderSection(providerName, examples) {
        let wrap = document.createDocumentFragment();
        let providerTitle = make('h2');
        let list = make('pre');

        providerTitle.innerText = providerName;
        providerTitle.className = 'provider-name no-select';

        list.innerText = examples.join('\n');
        wrap.appendChild(providerTitle);
        wrap.appendChild(list);

        return wrap
    }

    global.init = init;
})(window.DEUTSCH || (window.DEUTSCH = {}));

window.addEventListener('DOMContentLoaded', DEUTSCH.init);
