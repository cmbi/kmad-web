import os
import subprocess

from kmad_web.services.types import ServiceError
from kmad_web.services.helpers.cache import cache_manager as cm


class NetphosService(object):
    def __init__(self, path=None):
        self._path = path

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, path):
        self._path = path

    @cm.cache('redis')
    def predict(self, fasta_filename):
        try:
            netphos_exists = os.path.exists(self._path)
            fasta_exists = os.path.exists(fasta_filename)
            if netphos_exists and fasta_exists:
                args = [self._path, fasta_filename]
                result = subprocess.check_output(args, stderr=subprocess.PIPE)
            elif not netphos_exists:
                raise ServiceError("Netphos not found: {}".format(self._path))
            else:
                raise ServiceError("File not found: {}".format(fasta_filename))
        except subprocess.CalledProcessError as e:
            raise ServiceError(e)
        return result

netphos = NetphosService()
