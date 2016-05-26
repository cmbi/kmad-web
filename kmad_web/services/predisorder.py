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
        errlog_name = out_file + "_errlog"
        try:
            with open(errlog_name, 'w') as err:
                subprocess.call(args, stderr=err)
            # remove error log file if it's empty, otherwise raise an error
            empty_errlog = os.stat(errlog_name).st_size == 0
            os.remove(fasta_filename)
            if not empty_errlog:
                e = "Predisorder raised an error, check logfile: {}".format(
                    errlog_name)
                _log.warning(e)
            else:
                os.remove(empty_errlog)
            if os.path.exists(out_file):
                with open(out_file) as a:
                    data = a.read()
                # os.remove(out_file)
                return data
            else:
                e = "Didn't find the output file: {}".format(out_file)
                _log.error(e)
                raise ServiceError(e)
        except subprocess.CalledProcessError as e:
            _log.error(e)
            raise ServiceError(e.message)

predisorder = PredisorderService(PREDISORDER)
