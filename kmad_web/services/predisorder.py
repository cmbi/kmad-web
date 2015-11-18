import logging
import os
import subprocess

from kmad_web.default_settings import PREDISORDER
from kmad_web.services.types import ServiceError
from kmad_web.services.helpers.cache import cache_manager as cm

_log = logging.getLogger(__name__)


class PredisorderService(object):
    def __init__(self, path):
        self._path = path

    @cm.cache('redis')
    def __call__(self, fasta_filename):
        _log.info("Calling PredisorderService")
        out_file = '.'.join(fasta_filename.split('.')[:-1])+".predisorder"
        args = [self._path, fasta_filename, out_file]
        try:
            subprocess.call(args)
            if os.path.exists(out_file):
                with open(out_file) as a:
                    data = a.read()
                return data
            else:
                raise ServiceError("Didn't find the output file: {}".format(
                    out_file))
        except subprocess.CalledProcessError as e:
            raise ServiceError(e.message)

predisorder = PredisorderService(PREDISORDER)
