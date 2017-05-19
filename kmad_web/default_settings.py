from celery.schedules import crontab
from kombu import Exchange, Queue


# Celery
CELERY_BROKER_URL = 'amqp://guest@kmadweb_rabbitmq_1'
CELERY_DEFAULT_QUEUE = 'kmad_web'
CELERY_QUEUES = (
    Queue('kmad_web', Exchange('kmad_web'), routing_key='kmad_web'),
)
CELERY_RESULT_BACKEND = 'redis://kmadweb_redis_1/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERYBEAT_SCHEDULE = {
    # Every month on the 1st at midnight
    'update_elmdb': {
        'task': 'kmad_web.tasks.update_elmdb',
        'schedule': crontab(day_of_month=1, hour=0, minute=0),
        'args': ()
    },
    'remove_old_tmps': {
        'task': 'kmad_web.tasks.remove_old_tmps',
        'schedule': crontab(hour=13, minute=0),
        'args': ()
    },
}

# Cache (dogpile)
CACHE_CONFIG = {
    'redis': {
        'redis.backend': 'dogpile.cache.redis',
        'redis.arguments.host': 'kmadweb_redis_1',
        'redis.arguments.port': 6379,
        'redis.arguments.db': 1,
        'redis.arguments.redis_expiration_time': 60*60*24*30,  # 30 days
        'redis.arguments.distributed_lock': True
    }
}

CELERYD_CONCURRENCY = 8
CELERYD_NODES = 3

# service urls
ELM_URL = "http://elm.eu.org"
GO_URL = "http://www.ebi.ac.uk/ols/api/ontologies/go/terms/http%253A%252F%252Fpurl.obolibrary.org%252Fobo%252F"

UNIPROT_URL = "http://www.uniprot.org/uniprot"
UNIPROT_PTMS_URL = "http://www.uniprot.org/docs/ptmslist.txt"
PFAM_URL = "http://pfam.xfam.org/search/sequence"
PFAM_ID_URL = "http://pfam.xfam.org/protein/{}?output=xml"
D2P2_URL = "http://d2p2.pro/api/seqid"
KMAD = "/usr/local/bin/kmad"

# paths
ELMDB_PATH = 'kmad_web/frontend/static/dbs/elm_complete.txt'
NETPHOS_PATH = '/usr/local/bin/netphos'
CLUSTALO = '/usr/local/bin/clustalo'
CLUSTALW = '/usr/local/bin/clustalw2'
MAFFT = '/usr/local/bin/mafft'
MUSCLE = '/usr/local/bin/muscle'
TCOFFEE = '/usr/local/bin/t_coffee'

# predictors
IUPRED = "/srv/kmad/iupred/iupred"
IUPRED_DIR = "/srv/kmad/iupred/"
SPINED = "/srv/kmad/spined/bin/run_spine-d"
SPINED_OUTPUT_DIR = "/srv/kmad/spined/predout/"
DISOPRED = "/deps/disopred/run_disopred.pl"
PREDISORDER = "/srv/kmad/predisorder/bin/predict_diso.sh"
PSIPRED = "/srv/kmad/psipred4.0/runpsipred"
GLOBPLOT = "/usr/local/bin/GlobPipe.py"
BLAST_DB = "/data/blast/sprot"
BLASTP = "/usr/local/bin/blastp"
