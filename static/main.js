(function (global) {

    function $(selector, context) {
        return (context || document).querySelector(selector)
    }

    function $$(selector, context) {
        return [].slice.call((context || document).querySelectorAll(selector))
    }

    function make(type) {
        return document.createElement(type);
    }

    function init() {
        let searchForm = $('.search');
        let searchInput = $('[name=q]', searchForm);
        let submit = $('button', searchForm);
        let examplesContainer = $('.examples');
        let providers = $$('[type=checkbox]', searchForm);

        searchForm.addEventListener('submit', handleSubmit);
        window.addEventListener('keydown', handleKeydown);
        window.addEventListener('paste', handlePaste);

        function handleSubmit(e) {
            e.preventDefault();

            let term = searchInput.value;
            if (!term) return;

            providersList = providers
                .filter(p => p.checked)
                .map(p => p.value);
            examplesContainer.innerText = '';
            fetchExamples(term, providersList, providerResponded);
        }

        function providerResponded(data) {
            let section = makeProviderSection(data);
            examplesContainer.appendChild(section)
        }

        function handleKeydown(e) {
            if (e.key === 'Escape') {
                searchInput.focus();
                searchInput.select();
            }
        }

        function handlePaste(e) {
            e.preventDefault();
            let paste = (e.clipboardData || window.clipboardData).getData('text').trim();
            searchInput.value = paste;
            submit.click();
        }
    }


    function fetchExamples(term, providersList, callback) {
        providersList.forEach(provider => {
            fetch(`/examples/${provider}/${term}`)
                .then(res => res.json())
                .then(callback)
                .catch(console.log)
        });
    }

    function makeProviderSection(data) {
        let section = make('section');
        let title = make('h2');
        let pre = make('pre');

        title.innerHTML = `${data.term} <a class="provider-name dim" 
                                            target="_blank" 
                                            href="${data.url}">${data.provider}</a>`;
        title.className = 'no-select';

        if (!data.examples.length) {
            section.className = 'no-select dim';
            pre.innerText = '(no examples)';
        } else {
            pre.innerText = data.examples.join('\n');
        }
        section.appendChild(title);
        section.appendChild(pre);

        return section
    }

    global.init = init;
})(window.DEUTSCH || (window.DEUTSCH = {}));

window.addEventListener('DOMContentLoaded', DEUTSCH.init);
