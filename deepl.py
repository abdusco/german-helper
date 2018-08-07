from requests import Response, post
from werkzeug.exceptions import ServiceUnavailable
from errors import MissingContent


def get_translations(phrase: str) -> list:
    url = 'https://www2.deepl.com/jsonrpc'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:62.0) Gecko/20100101 Firefox/62.0',
        'Referer': 'https://www.deepl.com/translator',
    }
    try:
        response: Response = post(url, headers=headers, json={
            'jsonrpc': 2.0,
            'method': 'LMT_handle_jobs',
            'params': {
                'jobs': [
                    {
                        'kind': 'default',
                        'raw_en_sentence': phrase
                    }
                ],
                'lang': {
                    # 'user_preferred_langs': [
                    #     'EN',
                    #     'DE'
                    # ],
                    'source_lang_user_selected': 'DE',
                    'target_lang': 'EN'
                },
                # 'priority': -1
            },
            # 'id': 10
        })

        data = response.json()
        translations = data['result']['translations'][0]['beams']
        translations = [t['postprocessed_sentence']
                        for t in sorted(translations, key=lambda a: -a['score'])]
        return translations
    except KeyError:
        raise MissingContent
    except:
        raise ServiceUnavailable


if __name__ == '__main__':
    print(get_translations('Ich will weg'))
