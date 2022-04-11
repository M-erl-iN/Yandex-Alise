from flask import Flask, request
import logging
import json

yes_repr = [
        'ладно',
        'куп',
        'хорошо',
        'хот',
        'хоч'
    ]

no_repr = [
        'не',
        'хуй',
        'отстань'
    ]

animals = ['слон', 'кролик']
animals_index = 0
url_ = "https://market.yandex.ru/search?text="

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)
sessionStorage = {}


@app.route('/', methods=['POST'])
def main():
    logging.info(f'Request: {request.json!r}')
    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }

    # Отправляем request.json и response в функцию handle_dialog.
    # Она сформирует оставшиеся поля JSON, которые отвечают
    # непосредственно за ведение диалога
    handle_dialog(request.json, response)

    logging.info(f'Response:  {response!r}')

    # Преобразовываем в JSON и возвращаем
    return json.dumps(response)


def handle_dialog(req, res):
    global animals_index
    user_id = req['session']['user_id']

    if req['session']['new']:
        sessionStorage[user_id] = {
            'suggests': [
                "Не хочу.",
                "Не буду.",
                "Отстань!",
            ]
        }
        res['response']['text'] = f'Привет! Купи {animals[animals_index]}а!'
        res['response']['buttons'] = get_suggests(user_id)
        return
    replica = req['request']['original_utterance'].lower()
    if any([i in replica for i in yes_repr]) and all([i not in replica for i in no_repr]):
        res['response']['text'] = f'{animals[animals_index]}а можно найти на Яндекс.Маркете!'
        animals_index = (animals_index + 1) % 2
        return
    res['response']['text'] = \
        f"Все говорят '{req['request']['original_utterance']}', а ты купи {animals[animals_index]}а!"
    res['response']['buttons'] = get_suggests(user_id)


# Функция возвращает две подсказки для ответа.
def get_suggests(user_id):
    global animals_index
    session = sessionStorage[user_id]

    # Выбираем две первые подсказки из массива.
    suggests = [
        {'title': suggest, 'hide': True}
        for suggest in session['suggests'][:2]
    ]

    # Убираем первую подсказку, чтобы подсказки менялись каждый раз.
    session['suggests'] = session['suggests'][1:]
    sessionStorage[user_id] = session

    # Если осталась только одна подсказка, предлагаем подсказку
    # со ссылкой на Яндекс.Маркет.
    if len(suggests) < 2:
        suggests.append({
            "title": "Ладно",
            "url": f"https://market.yandex.ru/search?text={animals[animals_index]}",
            "hide": True
        })

    return suggests


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
