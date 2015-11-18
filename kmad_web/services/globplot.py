import logging
import os
import subprocess
import tempfile

from kmad_web.default_settings import GLOBPLOT
from kmad_web.services.types import ServiceError
from kmad_web.services.helpers.cache import cache_manager as cm

_log = logging.getLogger(__name__)


class GlobplotService(object):
    def __init__(self, path):
        self._path = path

    @cm.cache('redis')
    def __call__(self, fasta_sequence):
        _log.info("Calling GlobplotService")

        tmp_file = tempfile.NamedTemporaryFile(suffix=".fasta", delete=False)
        with tmp_file as f:
            f.write(fasta_sequence)
        fasta_filename = tmp_file.name

        args = [self._path, '10', '8', '75', '8', '8',
                fasta_filename]
        try:
            data = subprocess.check_output(args)
            _log.info("filename: {}".format(fasta_filename))
            if not data or not data.startswith('>'):
                raise ServiceError("No prediction was returned,"
                                   " command: {}".format(subprocess.list2cmdline(args))
                                   )
            return data
        except subprocess.CalledProcessError as e:
            raise ServiceError(e.message)


globplot = GlobplotService(GLOBPLOT)
