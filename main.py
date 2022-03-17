import os

from flask import Flask, request
import logging
import json
import random

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

# создаем словарь, в котором ключ — название города,
# а значение — массив, где перечислены id картинок,
# которые мы записали в прошлом пункте.

cities = {
    'москва': ['937455/a7a2cfc9606257829dca',
               '213044/e6fbe791701703669d9e'],
    'нью-йорк': ['937455/ab764af94fe9d354271f',
                 '213044/416f8b14285d029c475c'],
    'париж': ["1652229/cf953c4ca0682bc21b53",
              '1521359/f78a2ad14d9cb6e35be8']
}

yes_or_no = {
    'ДА': 1,
    'нет': 0
}
# создаем словарь, где для каждого пользователя
# мы будем хранить его имя
sessionStorage = {}


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
    play_game(response, request.json)
    logging.info(f'Response: {response!r}')
    return json.dumps(response)


def play_game(res, req):
    user_id = req['session']['user_id']

    # если пользователь новый, то просим его представиться.
    if req['session']['new']:
        res['response']['text'] = 'Привет! Назови свое имя!'
        # создаем словарь в который в будущем положим имя пользователя
        sessionStorage[user_id] = {
            'first_name': None,
            'city': None
        }
        return

    # если пользователь не новый, то попадаем сюда.
    # если поле имени пустое, то это говорит о том,
    # что пользователь еще не представился.
    if sessionStorage[user_id]['first_name'] is None:
        # в последнем его сообщение ищем имя.
        first_name = get_first_name(req)
        # если не нашли, то сообщаем пользователю что не расслышали.
        if first_name is None:
            res['response']['text'] = \
                'Не расслышала имя. Повтори, пожалуйста!'
        # если нашли, то приветствуем пользователя.
        # И спрашиваем какой город он хочет увидеть.
        else:
            sessionStorage[user_id]['first_name'] = first_name
            res['response'][
                'text'] = 'Приятно познакомиться, ' \
                          + first_name.title() \
                          + '. Я - Алиса. Хочешь угадать город??'
            # получаем варианты buttons из ключей нашего словаря cities
            res['response']['buttons'] = [
                {
                    'title': city.title(),
                    'hide': True
                } for city in yes_or_no
            ]
    else:
        result = get_city(req)
        # если этот город среди известных нам,
        # то показываем его (выбираем одну из двух картинок случайно)
        if result == 1:
            city = random.choice(['москва', 'нью-йорк', 'париж'])
            random_city = random.choice(cities[city])
            res['response']['card'] = {}
            res['response']['card']['type'] = 'BigImage'
            res['response']['card']['title'] = 'Что это за город?'
            res['response']['card']['image_id'] = random_city
            res['response']['text'] = 'Угадай'
            res['response']['buttons'] = [
                {
                    'title': city.title(),
                    'hide': True
                } for city in cities
            ]
            sessionStorage[user_id]['city'] = city
        elif result == 0:
            res['response']['text'] = 'Ну и ладно... Пока!!!'
            res['end_session'] = True
        elif result == 'москва':
            if sessionStorage[user_id]['city'] == 'москва':
                res['response'][
                    'text'] = 'Правильно! Продолжим?'
                res['response']['buttons'] = [
                    {
                        'title': city.title(),
                        'hide': True
                    } for city in yes_or_no
                ]
            else:
                res['response'][
                    'text'] = 'Не верно! Повторим?'
                res['response']['buttons'] = [
                    {
                        'title': city.title(),
                        'hide': True
                    } for city in yes_or_no
                ]
        elif result == 'нью-йорк':
            if sessionStorage[user_id]['city'] == 'нью-йорк':
                res['response'][
                    'text'] = 'Правильно! Продолжим?'
                res['response']['buttons'] = [
                    {
                        'title': city.title(),
                        'hide': True
                    } for city in yes_or_no
                ]
            else:
                res['response'][
                    'text'] = 'Не верно! Повторим?'
                res['response']['buttons'] = [
                    {
                        'title': city.title(),
                        'hide': True
                    } for city in yes_or_no
                ]
        elif result == 'париж':
            if sessionStorage[user_id]['city'] == 'париж':
                res['response'][
                    'text'] = 'Правильно! Продолжим?'
                res['response']['buttons'] = [
                    {
                        'title': city.title(),
                        'hide': True
                    } for city in yes_or_no
                ]
            else:
                res['response'][
                    'text'] = 'Не верно! Повторим?'
                res['response']['buttons'] = [
                    {
                        'title': city.title(),
                        'hide': True
                    } for city in yes_or_no
                ]
        else:
            res['response']['text'] = 'Не поняла ответа! Так да или нет?'
            res['response']['buttons'] = [
                {
                    'title': city.title(),
                    'hide': True
                } for city in yes_or_no
            ]

    # если мы знакомы с пользователем и он нам что-то написал,
    # то это говорит о том, что он уже говорит о городе,
    # что хочет увидеть.


def get_city(req):
    # перебираем именованные сущности
    if 'да' in req['request']['nlu']['tokens']:
        return 1
    if 'нет' in req['request']['nlu']['tokens']:
        return 0
    for entity in req['request']['nlu']['entities']:
        # если тип YANDEX.GEO то пытаемся получить город(city),
        # если нет, то возвращаем None
        if entity['type'] == 'YANDEX.GEO':
            # возвращаем None, если не нашли сущности с типом YANDEX.GEO
            return entity['value'].get('city', None)


def get_first_name(req):
    # перебираем сущности
    for entity in req['request']['nlu']['entities']:
        # находим сущность с типом 'YANDEX.FIO'
        if entity['type'] == 'YANDEX.FIO':
            # Если есть сущность с ключом 'first_name',
            # то возвращаем ее значение.
            # Во всех остальных случаях возвращаем None.
            return entity['value'].get('first_name', None)


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
