import logging
import os
import subprocess
import tempfile

from kmad_web.services.types import ServiceError
from kmad_web.services.helpers.cache import cache_manager as cm

_log = logging.getLogger(__name__)


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
    def predict(self, fasta_sequence):
        _log.info("Getting prediction from NetPhos")
        try:
            tmp_file = tempfile.NamedTemporaryFile(
                suffix=".fasta", delete=False)
            with tmp_file as f:
                f.write(fasta_sequence)
            fasta_filename = tmp_file.name

            netphos_exists = os.path.exists(self._path)
            if netphos_exists:
                args = [self._path, fasta_filename]
                _log.debug("Calling NetPhos with command {}".format(
                    subprocess.list2cmdline(args)
                ))
                result = subprocess.check_output(args, stderr=subprocess.PIPE)
                os.remove(fasta_filename)
            else:
                raise ServiceError("Netphos not found: {}".format(self._path))
        except subprocess.CalledProcessError as e:
            raise ServiceError(e)
        return result

netphos = NetphosService()
