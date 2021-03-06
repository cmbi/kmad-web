import logging
import os
import subprocess
import tempfile

from kmad_web.default_settings import BLASTP
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
        self._outfmt = "10 qseqid sseqid pident mismatch evalue bitscore slen" \
                       " qlen"

    """
    Runs blast and writes it to self.result

    :param fasta_filename: path to the query fasta file
    """
    @cm.cache('redis')
    def run_blast(self, fasta_sequence, seq_limit):
        _log.info("Running BLAST [service]")
        tmp_file = tempfile.NamedTemporaryFile(suffix=".fasta", delete=False)
        with tmp_file as f:
            f.write(fasta_sequence)
        fasta_filename = tmp_file.name

        args = [BLASTP, '-query', fasta_filename, '-evalue', '1e-5',
                '-num_threads', '15', '-db', self._db_path,
                '-outfmt', self._outfmt, '-max_target_seqs', str(seq_limit)]
        try:
            _log.debug("Running BLAST with command %s",
                       subprocess.list2cmdline(args))
            result = subprocess.check_output(args)
            os.remove(fasta_filename)
            return result
        except subprocess.CalledProcessError as e:
            _log.error("BlastService returned an error: %s", e)
            raise ServiceError(e)
