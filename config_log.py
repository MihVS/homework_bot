LOGGER_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,

    'formatters': {
        'my_format': {
            'format': '{asctime} - '
                      '{levelname} - '
                      '{name} - '
                      '{module}:{funcName}:{lineno} - '
                      '{message}',
            'style': '{'
        }
    },

    'handlers': {
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'INFO',
            'formatter': 'my_format',
            'filename': 'log.log',
            'maxBytes': 50000000,
            'backupCount': 5,
            'encoding': 'utf8'
        },
        'std': {
            'class': 'logging.StreamHandler',
            'level': 'NOTSET',
            'formatter': 'my_format'
        }
    },

    'loggers': {
        'bot_logger': {
            'level': 'DEBUG',
            'handlers': ['file', 'std']
        }
    }
}
