from celery.schedules import crontab
from kombu import Exchange, Queue


# Celery
CELERY_BROKER_URL = 'amqp://guest@localhost'

CELERY_DEFAULT_QUEUE = 'kmad_web'
CELERY_QUEUES = (
    Queue('kmad_web', Exchange('kmad_web'), routing_key='kmad_web'),
)
CELERY_RESULT_BACKEND = 'redis://localhost/2'

CELERYBEAT_SCHEDULE = {
    # Every month on the 1st at midnight
    'update_elmdb': {
        'task': 'kmad_web.tasks.update_elmdb',
        'schedule': crontab(day_of_month=1, hour=0, minute=0),
        'args': ('kmad_web/frontend/static/dbs/elm_complete.txt',)
    },
}

# service urls
ELM_URL = "http://elm.eu.org"
GO_URL = "http://www.ebi.ac.uk/ontology-lookup/OntologyQuery.wsdl"
UNIPROT_URL = "http://www.uniprot.org/uniprot"
PFAM_URL = "http://pfam.xfam.org/search/sequence"
KMAD = "kmad"

# paths
ELMDB_PATH = 'kmad_web/frontend/static/dbs/elm_complete.txt'
NETPHOS_PATH = '/usr/local/bin/netphos'
CLUSTALO = '/usr/bin/clustalo'
CLUSTALW = '/usr/local/bin/clustalw2'
MUSCLE = '/usr/local/bin/muscle'
MAFFT = '/usr/local/bin/mafft'
TCOFFEE = '/usr/local/bin/t_coffee'
# predictors
IUPRED = ""
IUPRED_DIR = ""
SPINE = "/srv/kmad/spined/spined"
SPINE_OUTPUT_DIR = "/srv/kmad/spined/predout/"
DISOPRED = ""
PREDISORDER = ""
PSIPRED = ""
GLOBPLOT = ""
BLAST_DB = "/home/joanna/data/uniprot_sprot"
