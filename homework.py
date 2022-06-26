import logging.config
import os
import time
from http import HTTPStatus

import requests
import telegram
from dotenv import load_dotenv

from config_log import LOGGER_CONFIG
from exceptions import ENVError, RequestAPIYandexPracticumError

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

message_cash = ''


def send_message(bot, message):
    """Отправляет сообщение в Telegram чат."""
    global message_cash
    try:
        if message_cash != message:
            bot.send_message(TELEGRAM_CHAT_ID, message)
            message_cash = message
            _logger.info('Сообщение в телеграм отправлено')
        else:
            _logger.debug('Сообщение в телеграм не отправлено, '
                          'т.к. не изменилось')
    except telegram.TelegramError:
        _logger.error('Сообщение в телеграм не отправлено')


def get_api_answer(current_timestamp: int) -> dict:
    """Делает запрос к API-сервису."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    homework_statuses = requests.get(
        ENDPOINT, headers=HEADERS, params=params
    )
    if homework_statuses.status_code != HTTPStatus.OK:
        raise RequestAPIYandexPracticumError(
            'API практикума не доступен'
        )
    _logger.debug('Запрос к API практикума выполнен успешно')
    return homework_statuses.json()


def check_response(response: dict) -> list:
    """
    Проверяет ответ API на корректность.
    В качестве параметра функция получает ответ API.
    """
    if not isinstance(response, dict):
        raise TypeError('response должен быть dict')

    if 'homeworks' not in response:
        raise KeyError('API практикума вернул неожидаемое значение')

    if not isinstance(response['homeworks'], list):
        raise TypeError('Тип значения "homeworks" не list')

    list_homeworks = response['homeworks']

    if not list_homeworks:
        _logger.debug('Получен пустой список домашних работ')
    else:
        _logger.debug('Получен список домашних работ')
    return list_homeworks


def parse_status(homework: dict) -> str:
    """Извлекает из информации о конкретной
    домашней работе статус этой работы."""
    if 'homework_name' not in homework:
        raise KeyError('Не удалось спарсить имя домашней работы')

    homework_name = homework['homework_name'].split('.')[0]
    _logger.debug(f'Название домашней работы - {homework_name}')

    if 'status' not in homework:
        raise KeyError('Не удалось спарсить статус домашней работы')

    homework_status = homework['status']
    _logger.debug(f'Статус домашней работы - {homework_status}')

    if 'reviewer_comment' not in homework:
        raise KeyError('Не удалось спарсить комментарий ревьюера')

    reviewer_comment = homework['reviewer_comment']
    _logger.debug(f'Коммент по домашке от ревью - {reviewer_comment}')

    if homework_status not in HOMEWORK_STATUSES:
        raise KeyError(
            f'Получен неизвестный статус домашней работы - {homework_status}'
        )

    verdict = HOMEWORK_STATUSES[homework_status]
    _logger.debug(f'Вердикт - {verdict}')

    return (
        f'Изменился статус проверки работы "{homework_name}". {verdict}'
        # f' Комментарий от ревьюера: {reviewer_comment}'
    )


def check_tokens() -> bool:
    """Проверяет доступность переменных окружения."""
    if PRACTICUM_TOKEN and TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
        _logger.debug('Переменные окружения доступны')
        return True

    return False


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        _logger.error('Переменные окружения недоступны, проверьте файл .env')
        raise ENVError('Токены не найдены в файле .env')

    global message_cash

    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())

    while True:
        try:
            response = get_api_answer(current_timestamp)
            if not response:
                raise RequestAPIYandexPracticumError

            list_homeworks = check_response(response)

            if list_homeworks:
                message = parse_status(list_homeworks[0])
                send_message(bot, message)

            current_timestamp = response['current_date']
            time.sleep(RETRY_TIME)

        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            _logger.error(message)
            send_message(bot, message)
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
