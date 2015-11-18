import logging
import subprocess

from kmad_web.default_settings import IUPRED, IUPRED_DIR
from kmad_web.services.types import ServiceError
from kmad_web.services.helpers.cache import cache_manager as cm

_log = logging.getLogger(__name__)


class IupredService(object):
    def __init__(self, path, iupred_dir):
        self._path = path
        self._dir = iupred_dir

    @cm.cache('redis')
    def __call__(self, fasta_filename):
        _log.info("Calling IupredService")
        args = [self._path, fasta_filename, 'long']
        env = {"IUPred_PATH": self._dir}
        try:
            data = subprocess.check_output(args, env=env)
            if not data:
                raise ServiceError("No prediction was returned")
            return data
        except subprocess.CalledProcessError as e:
            raise ServiceError(e.message)

iupred = IupredService(IUPRED, IUPRED_DIR)
