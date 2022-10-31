# homework_bot


## Описание

Телеграм бот опрашивает API сервиса Практикум.Домашка и проверяет статус отправленной на ревью домашней работы.

При изменении статуса отправляет личное сообщение в telegram.


## **Технологии**
![python version](https://img.shields.io/badge/Python-3.9-yellowgreen?logo=python)
![python-telegram-bot version](https://img.shields.io/badge/telegram_bot-13.7-yellowgreen?logo=telegram)
![requests version](https://img.shields.io/badge/requests-2.26-yellowgreen)

## Запуск бота:

1. Клонировать репозиторий и перейти в него в командной строке.

2. Cоздать и активировать виртуальное окружение:

```
python3 -m venv venv
```

```
source venv/bin/activate
```

```
python3 -m pip install --upgrade pip
```

3. Установить зависимости из файла requirements.txt:

```
pip install -r requirements.txt
```

4. Создать файл .env и заполнить его по примеру .env_example:

```
touch .env
```

Запустить проект:

```
python3 homework.py
```

## Заполнение файла .env:

- PRACTICUM_TOKEN - для получения токена авторизируйтесь [тут]( https://oauth.yandex.ru/authorize?response_type=token&client_id=1d0b9dd4d652455a9eb710d450ff456a)

- TELEGRAM_TOKEN - токен Вашего бота.
  * в telegram боту @BotFather отправить ```Start```
  * далее создаем нового бота командой ```/newbot```
  * @BotFather в ответ отправит вам токен.  Токен выглядит примерно так: 123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11.
  
- TELEGRAM_CHAT_ID - id вашего чата.  Л
  * можно спросить у бота @userinfobot командой ```/start```

## Логи

Приложение выводит логи в консоль и пишет в файл ```log.log```
Изменить уровень логирования можно в конфигурационном файле ```config_log.py```
