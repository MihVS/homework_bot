import json
import logging.config
import os
import time
from pprint import pprint

import requests
from http import HTTPStatus

from dotenv import load_dotenv

from config_log import LOGGER_CONFIG
from exceptions import RequestAPIYandexPracticumError

load_dotenv()

logging.config.dictConfig(LOGGER_CONFIG)
_logger = logging.getLogger('bot_logger')


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def send_message(bot, message):
    """Отправляет сообщение в Telegram чат."""
    pass


def get_api_answer(current_timestamp: int) -> dict:
    """Делает запрос к API-сервису."""

    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    try:
        homework_statuses = requests.get(
            ENDPOINT, headers=HEADERS, params=params
        )
        if homework_statuses.status_code != HTTPStatus.OK:
            raise RequestAPIYandexPracticumError(
                'API практикума не доступен'
            )
        _logger.debug('Запрос к API практикума выполнен успешно')
        return json.loads(homework_statuses.text)
    except RequestAPIYandexPracticumError:
        _logger.error(f'код ответа API практикума '
                      f'{homework_statuses.status_code}'
                      )
    except requests.exceptions.ConnectionError:
        _logger.error('Ошибка соединения с url API практикума')
    return {}


def check_response(response: dict) -> list:
    """
    Проверяет ответ API на корректность.
    В качестве параметра функция получает ответ API.
    """

    list_homeworks: list = []

    try:
        list_homeworks = response['homeworks']
        if not list_homeworks:
            _logger.debug('Получен пустой список домашних работ')
        else:
            _logger.debug('Получен список домашних работ')
    except (IndexError, TypeError, KeyError):
        _logger.error('API практикума вернул неожидаемое значение')
    return list_homeworks


def parse_status(homework: dict) -> str:
    """
    Извлекает из информации о конкретной домашней работе статус этой работы.
    """

    try:
        homework_name = homework['homework_name'].split('.')[0]
        _logger.debug(f'Название домашней работы - {homework_name}')
        homework_status = homework['status']
        _logger.debug(f'Статус домашней работы - {homework_status}')
    except KeyError:
        _logger.error('Не удалось спарсить статус домашней работы')
        homework_status = 'Статус неизвестен'
        homework_name = 'Имя не известно'

    try:
        verdict = HOMEWORK_STATUSES[homework_status]
        _logger.debug(f'Статус домашней работы - {verdict}')
    except KeyError:
        _logger.error(
            f'Получен неизвестный статус домашней работы - {homework_name}'
        )
        verdict = 'ВЕРДИКТ НЕИЗВЕСТЕН'

    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    ...


def main():
    """Основная логика работы бота."""

    ...

    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())

    ...

    while True:
        try:
            response = ...

            ...

            current_timestamp = ...
            time.sleep(RETRY_TIME)

        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            ...
            time.sleep(RETRY_TIME)
        else:
            ...


def test_logger():
    _logger.debug('Уровень дебаг = 10')
    _logger.info('Уровень инфо = 20')
    _logger.warning('Уровень варнинг = 30')
    _logger.error('Уровень еррор = 40')
    _logger.critical('Уровень критикал = 50')


if __name__ == '__main__':
    # main()
    home_work = check_response(get_api_answer(current_timestamp=1))[0]
    print(parse_status({}))
