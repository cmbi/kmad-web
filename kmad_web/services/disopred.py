import logging
import os
import subprocess
import tempfile

from kmad_web.default_settings import DISOPRED
from kmad_web.services.types import ServiceError
from kmad_web.services.helpers.cache import cache_manager as cm

_log = logging.getLogger(__name__)


class DisopredService(object):
    def __init__(self, path):
        self._path = path

    @cm.cache('redis')
    def __call__(self, fasta_sequence):
        _log.info("Calling DisopredService")

        tmp_file = tempfile.NamedTemporaryFile(suffix=".fasta", delete=False)
        with tmp_file as f:
            f.write(fasta_sequence)
        fasta_filename = tmp_file.name

        out_file = '.'.join(fasta_filename.split('.')[:-1])+".diso"
        args = [self._path, fasta_filename]
        errlog_name = out_file + "_errlog"
        try:
            with open(errlog_name) as err:
                subprocess.call(args, stderr=err)
            # remove error log file if it's empty, otherwise raise an error
            empty_errlog = os.stat(errlog_name).st_size == 0
            if empty_errlog:
                os.remove(empty_errlog)
                os.remove(fasta_filename)
            else:
                e = "Disopred raised an error, check logfile: {}".format(
                    errlog_name)
                _log.error(e)
                raise ServiceError(e)
            os.remove(fasta_filename)
            if os.path.exists(out_file):
                with open(out_file) as a:
                    data = a.read()
                os.remove(out_file)
                return data
            else:
                _log.error("Didn't find the output file: %s", out_file)
                raise ServiceError("Didn't find the output file: %s", out_file)
        except (subprocess.CalledProcessError, OSError) as e:
            _log.error(e)
            raise ServiceError(e.message)

disopred = DisopredService(DISOPRED)
