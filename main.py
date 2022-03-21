import os

from flask import Flask, request
import logging

import json

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

sessionStorage = {}
elephant_status = False


@app.route('/post', methods=['POST'])
def main():
    logging.info(f'Request: {request.json!r}')

    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }

    handle_dialog(request.json, response)

    logging.info(f'Response:  {response!r}')

    return json.dumps(response)


def handle_dialog(req, res):
    global elephant_status
    user_id = req['session']['user_id']
    if elephant_status:
        ani = 'кролика'
    else:
        ani = 'слона'
    if req['session']['new']:

        sessionStorage[user_id] = {
            'suggests': [
                "Не хочу.",
                "Не буду.",
                "Отстань!",
            ]
        }
        res['response']['text'] = 'Привет! Купи ' + ani + '!'
        res['response']['buttons'] = get_suggests(user_id)
        return

    if req['request']['original_utterance'].lower() in [
        'Я покупаю',
        'Я куплю',
        'ладно',
        'куплю',
        'покупаю',
        'хорошо'
    ]:
        res['response']['text'] = ani.capitalize() + ' можно найти на Яндекс.Маркете!'
        elephant_status = True
        return

    res['response']['text'] = \
        f"Все говорят '{req['request']['original_utterance']}', а ты купи "
    res['response']['text'] += ani + '!'
    res['response']['buttons'] = get_suggests(user_id)


def get_suggests(user_id):
    global elephant_status
    if elephant_status:
        ani = 'кролика'
    else:
        ani = 'слона'
    session = sessionStorage[user_id]

    suggests = [
        {'title': suggest, 'hide': True}
        for suggest in session['suggests'][:2]
    ]
    session['suggests'] = session['suggests'][1:]
    sessionStorage[user_id] = session

    if len(suggests) < 2:
        urll = 'https://market.yandex.ru/search?text=' + ani[:-1]
        suggests.append({
            "title": "Ладно",
            "url": urll,
            "hide": True
        })

    return suggests


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
