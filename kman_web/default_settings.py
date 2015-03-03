from kombu import Exchange, Queue

# Celery
CELERY_BROKER_URL = 'amqp://guest@localhost'

CELERY_DEFAULT_QUEUE = 'kman_web'
CELERY_QUEUES = (
    Queue('kman_web', Exchange('kman_web'), routing_key='kman_web'),
)
CELERY_RESULT_BACKEND = 'redis://localhost/2'

#CELERY_TASK_SERIALIZER = 'json'
