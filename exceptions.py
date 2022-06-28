class RequestAPIYandexPracticumError(Exception):
    """Статус ответа при запросе к API Яндекс Практикум отличается от 200"""
    pass


class ENVError(Exception):
    """Ошибка доступности переменных окружения"""
    pass
