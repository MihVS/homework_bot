import logging.config
import os
import time
from http import HTTPStatus

import requests
import telegram
from dotenv import load_dotenv

from config_log import LOGGER_CONFIG
from exceptions import (ENVError, RequestAPIYandexPracticumError,
                        SendMessageError)

load_dotenv()

logging.config.dictConfig(LOGGER_CONFIG)
_logger = logging.getLogger('bot_logger')


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_TIME = 60
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


VERDICTS_REVIEWER = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def send_message(bot, message):
    """Отправляет сообщение в Telegram чат."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        _logger.info(f'Сообщение в телеграм отправлено: {message}')
    except Exception as error:
        raise SendMessageError(f'Ошибка: {error}')


def get_api_answer(current_timestamp: int) -> dict:
    """Делает запрос к API-сервису."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    try:
        homework_statuses = requests.get(
            ENDPOINT, headers=HEADERS, params=params
        )
        if homework_statuses.status_code != HTTPStatus.OK:
            raise Exception
    except Exception:
        raise RequestAPIYandexPracticumError(
            'Ошибка запроса к API практикума.'
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

    if 'homeworks' and 'current_date' not in response:
        raise KeyError('API практикума вернул неожидаемое значение')

    list_homeworks = response['homeworks']

    if not isinstance(list_homeworks, list):
        raise TypeError('Тип значения "homeworks" не list')

    if not list_homeworks:
        _logger.debug('Получен пустой список домашних работ')
    else:
        _logger.debug('Получен список домашних работ')
    return list_homeworks


def parse_status(homework: dict) -> str:
    """
    Извлекает из информации о конкретной домашней работе статус этой работы.
    И возвращает строку подготовленную строку.
    """
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

    reviewer_comment = (f" Комментарий от ревьюера: "
                        f"{homework['reviewer_comment']}")
    _logger.debug(reviewer_comment)

    if homework_status not in VERDICTS_REVIEWER:
        raise KeyError(
            f'Получен неизвестный статус домашней работы - {homework_status}'
        )

    if homework_status == 'reviewing':
        reviewer_comment = ''

    verdict = VERDICTS_REVIEWER[homework_status]
    _logger.debug(f'Вердикт - {verdict}')

    return (
        f'Изменился статус проверки работы "{homework_name}". {verdict}'
        f'{reviewer_comment}'
    )


def check_tokens() -> bool:
    """Проверяет доступность переменных окружения."""
    return all([PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID])


def main():
    """Основная логика работы бота."""
    if check_tokens():
        _logger.debug('Переменные окружения доступны')
    else:
        raise ENVError('Переменные окружения недоступны, проверьте файл .env')

    message_cash = ''
    message = ''

    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())

    while True:
        try:
            if message and message != message_cash:
                send_message(bot, message)
                message_cash = message

            response = get_api_answer(current_timestamp)

            if not response:
                raise RequestAPIYandexPracticumError(
                    'Ответ от API практикума пустой'
                )

            list_homeworks = check_response(response)

            if list_homeworks:
                message = parse_status(list_homeworks[0])

            current_timestamp = response['current_date']

        except SendMessageError as error:
            _logger.error(f'Сообщение в телеграм не отправлено. {error}')

        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            _logger.error(message)

        finally:
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
