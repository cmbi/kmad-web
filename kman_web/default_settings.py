from celery.schedules import crontab
from kombu import Exchange, Queue


# Celery
CELERY_BROKER_URL = 'amqp://guest@localhost'

CELERY_DEFAULT_QUEUE = 'kman_web'
CELERY_QUEUES = (
    Queue('kman_web', Exchange('kman_web'), routing_key='kman_web'),
)
CELERY_RESULT_BACKEND = 'redis://localhost/2'

#CELERY_TASK_SERIALIZER = 'json'
CELERYBEAT_SCHEDULE = {
    # Every day at midnight
    'update_elmdb': {
        'task': 'kman_web.tasks.update_elmdb',
        'schedule': crontab(hour=0,minute=0),
        'args': ('kman_web/frontend/static/dbs/elm_complete.txt',)
    },
}
