"""
Локальные настройки для тестирования с SQLite
"""

from .settings import *

# Переопределяем базу данных на SQLite для локального тестирования
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

DEBUG = True 