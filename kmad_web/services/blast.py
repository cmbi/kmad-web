import logging
import subprocess

from kmad_web.services.types import ServiceError
from kmad_web.services.helpers.cache import cache_manager as cm


_log = logging.getLogger(__name__)


class BlastService(object):
    """
    :param db_path: path to the BLAST database;
    :param seq_limit: maximum number of sequences;
    """
    def __init__(self, db_path):
        self._db_path = db_path
        self.result = None
        self._outfmt = "10 qseqid sseqid pident mismatch evalue bitscore slen" \
                       " qlen"

    """
    Runs blast and writes it to self.result

    :param fasta_filename: path to the query fasta file
    """
    @cm.cache('redis')
    def run_blast(self, fasta_filename):
        args = ['blastp', '-query', fasta_filename, '-evalue', '1e-5',
                '-num_threads', '15', '-db', self._db_path,
                '-outfmt', self._outfmt]
        try:
            self.result = subprocess.check_output(args)
        except subprocess.CalledProcessError as e:
            raise ServiceError(e)
