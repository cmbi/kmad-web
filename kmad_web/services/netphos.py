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
        _log.debug("Getting prediction from NetPhos")
        try:
            tmp_file = tempfile.NamedTemporaryFile(
                suffix=".fasta", delete=False)
            with open(tmp_file.name, "w") as f:
                f.write(fasta_sequence)
            fasta_filename = tmp_file.name

            netphos_exists = os.path.exists(self._path)
            if netphos_exists:
                args = [self._path, fasta_filename]
                _log.debug("Calling NetPhos with command {}".format(
                    subprocess.list2cmdline(args)
                ))
                result = subprocess.check_output(
                    args, stderr=subprocess.PIPE
                ).decode("utf-8")
                if "netphos-3.1b prediction results" not in result:
                    raise ServiceError(f"Netphos run unsuccessful:\n{result}")

                os.remove(fasta_filename)
            else:
                _log.error("NetPhos not found: {}".format(self._path))
                raise ServiceError("Netphos not found: {}".format(self._path))
        except subprocess.CalledProcessError as e:
            _log.error("NetPhos service returned an error: {}".format(e))
            raise ServiceError(e)
        return result

netphos = NetphosService()
