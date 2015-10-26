from celery.schedules import crontab
from kombu import Exchange, Queue


# Celery
CELERY_BROKER_URL = 'amqp://guest@localhost'

CELERY_DEFAULT_QUEUE = 'kmad_web'
CELERY_QUEUES = (
    Queue('kmad_web', Exchange('kmad_web'), routing_key='kmad_web'),
)
CELERY_RESULT_BACKEND = 'redis://localhost/2'

#CELERY_TASK_SERIALIZER = 'json'
CELERYBEAT_SCHEDULE = {
    # Every day at midnight
    'update_elmdb': {
        'task': 'kmad_web.tasks.update_elmdb',
        'schedule': crontab(hour=0,minute=0),
        'args': ('kmad_web/frontend/static/dbs/elm_complete.txt',)
    },
}

ELM_URL = "http://elm.eu.org"
GO_URL = "http://www.ebi.ac.uk/ontology-lookup/OntologyQuery.wsdl"
ELM_DB = 'kmad_web/frontend/static/dbs/elm_complete.txt'
