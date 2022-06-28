class RequestAPIYandexPracticumError(Exception):
    """Статус ответа при запросе к API Яндекс Практикум отличается от 200"""
    pass


class ENVError(Exception):
    """Ошибка доступности переменных окружения"""
    pass


class SendMessageError(Exception):
    """Ошибка отправки сообщения в телеграм"""
    pass


class HomeWorkIsEmpty(Exception):
    """Список домашних работ пуст"""
    pass
