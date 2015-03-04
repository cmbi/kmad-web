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
<<<<<<< HEAD
CELERYBEAT_SCHEDULE = {
    # Every day at midnight
    'update_elmdb': {
        'task': 'kman_web.tasks.update_elmdb',
        'schedule': crontab(hour=0,minute=0),
        'args': ('kman_web/frontend/static/dbs/elm_complete.txt',)
    },
}


## KMAN
#SPINE_DIR = "/mnt/datas/joanna/disorderPredictionMethods/spine-d/SPINE-D-local/"
SPINE_DIR = "/home/joanna/software/SPINE-D-local/"
SPINE_OUTPUT_DIR = SPINE_DIR+"predout/"
#DISOPRED_PATH ="/mnt/datas/joanna/disorderPredictionMethods/disopred/rundisopred"
DISOPRED_PATH ="/home/joanna/software/DISOPRED/run_disopred.pl"
#PREDISORDER_PATH = "/mnt/datas/joanna/disorderPredictionMethods/predisorder/predisorder1.1/bin/predict_diso.sh"
PREDISORDER_PATH = "/home/joanna/software/predisorder1.1/bin/predict_diso.sh"
#PSIPRED_PATH = "/mnt/datas/joanna/disorderPredictionMethods/psipred/runpsipred"
PSIPRED_PATH = "/home/joanna/software/psipred/runpsipred"
SWISSPROT_DB = "/home/joanna/data/uniprot_sprot.fasta"
ELM_DB = "/home/joanna/skrypty/elm_classes.tsv"
PFAM_SCAN = "/home/joanna/bin/PfamScan/pfam_scan.pl"
PFAM_DB = "/home/joanna/data/Pfam"

UNIPROT_FASTA_DIR = "/home/joanna/data/uniprot_fasta/"
UNIPROT_DAT_DIR = "/home/joanna/data/uniprot_dat/"
extension = {"disopred":".diso", "psipred":".ss2", "predisorder": ".predisorder", "spine":".spd"}
=======
>>>>>>> 3055ed785fc1c05c5b6367fc894cb29091436f84
