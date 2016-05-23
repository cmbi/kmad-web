import logging
import os
import subprocess
import tempfile

from kmad_web.default_settings import IUPRED, IUPRED_DIR
from kmad_web.services.types import ServiceError
from kmad_web.services.helpers.cache import cache_manager as cm

_log = logging.getLogger(__name__)


class IupredService(object):
    def __init__(self, path, iupred_dir):
        self._path = path
        self._dir = iupred_dir

    @cm.cache('redis')
    def __call__(self, fasta_sequence):
        _log.info("Calling IupredService")

        tmp_file = tempfile.NamedTemporaryFile(suffix=".fasta", delete=False)
        with tmp_file as f:
            f.write(fasta_sequence)
        fasta_filename = tmp_file.name
        errlog_name = fasta_filename + "_errlog"

        args = [self._path, fasta_filename, 'long']
        env = {"IUPred_PATH": self._dir}
        try:
            with open(errlog_name) as err:
                data = subprocess.check_output(args, stderr=err, env=env)
            # remove error log file if it's empty, otherwise raise an error
            empty_errlog = os.stat(errlog_name).st_size == 0
            if empty_errlog:
                os.remove(empty_errlog)
                os.remove(fasta_filename)
            else:
                e = "IUPred raised an error, check logfile: {}".format(
                    errlog_name)
                _log.error(e)
                raise ServiceError(e)
            if not data:
                _log.error("No prediction was returned")
                raise ServiceError("No prediction was returned")
            return data
        except (subprocess.CalledProcessError, OSError) as e:
            _log.error(e.message)
            raise ServiceError(e.message)

iupred = IupredService(IUPRED, IUPRED_DIR)
