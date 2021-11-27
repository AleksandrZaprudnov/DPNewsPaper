import os
import redis
from celery import Celery
from celery.schedules import crontab
from .functions import get_env


red = redis.Redis(
    host=get_env('HOST'),
    port=get_env('PORT'),
    password=get_env('PASSWORD')
)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'NewsPaper.settings')

app = Celery('NewsPaper')
app.config_from_object('django.conf:settings', namespace='CELERY')

app.conf.news_for_week_from_monday_schedule = {
    'action_in_8_hour': {
        'task': 'tasks.news_week',
        'schedule': crontab(minute=0, hour=8, day_of_week='monday'),
    },
}

app.autodiscover_tasks()

