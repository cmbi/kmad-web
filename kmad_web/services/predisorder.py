import logging
import os
import subprocess
import tempfile

from kmad_web.default_settings import PREDISORDER
from kmad_web.services.types import ServiceError
from kmad_web.services.helpers.cache import cache_manager as cm

_log = logging.getLogger(__name__)


class PredisorderService(object):
    def __init__(self, path):
        self._path = path

    @cm.cache('redis')
    def __call__(self, fasta_sequence):
        _log.info("Calling PredisorderService")

        tmp_file = tempfile.NamedTemporaryFile(suffix=".fasta", delete=False)
        with tmp_file as f:
            f.write(fasta_sequence)
        fasta_filename = tmp_file.name

        out_file = '.'.join(fasta_filename.split('.')[:-1])+".predisorder"
        args = [self._path, fasta_filename, out_file]
        try:
            subprocess.call(args)
            os.remove(fasta_filename)
            if os.path.exists(out_file):
                with open(out_file) as a:
                    data = a.read()
                os.remove(out_file)
                return data
            else:
                _log.error("Didn't find the output file: {}".format(
                    out_file))
                raise ServiceError("Didn't find the output file: {}".format(
                    out_file))
        except subprocess.CalledProcessError as e:
            _log.error(e)
            raise ServiceError(e.message)

predisorder = PredisorderService(PREDISORDER)
