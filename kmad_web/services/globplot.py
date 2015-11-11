import subprocess

from kmad_web.default_settings import GLOBPLOT
from kmad_web.services.types import ServiceError
from kmad_web.services.helpers.cache import cache_manager as cm


class GlobplotService(object):
    def __init__(self, path):
        self._path = path

    @cm.cache('redis')
    def __call__(self, fasta_filename):
        args = [self._path, '10', '8', '75', '8', '8',
                fasta_filename]
        import time
        time.sleep(20)
        try:
            data = subprocess.check_output(args)
            if not data:
                raise ServiceError("No prediction was returned")
            return data
        except subprocess.CalledProcessError as e:
            raise ServiceError(e.message)

globplot = GlobplotService(GLOBPLOT)
