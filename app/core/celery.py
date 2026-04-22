import os
from celery import Celery

# Устанавливаем настройки Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# Создаем объект Celery (переменная должна называться именно app)
app = Celery('core')

# Загружаем конфиг из settings.py с префиксом CELERY
app.config_from_object('django.conf.settings', namespace='CELERY')

# Автопоиск задач tasks.py
app.autodiscover_tasks()