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
            _log.debug("running Predisorder: {}".format(' '.join(args)))
            with open(errlog_name, 'w') as err:
                subprocess.call(args, stderr=err)

            if os.path.exists(out_file):
                with open(out_file) as a:
                    data = a.read()
                return data
            else:
                e = "Didn't find the output file: {}".format(out_file)
                empty_errlog = os.stat(errlog_name).st_size == 0
                if not empty_errlog:
                    with open(errlog_name, 'r') as f:
                        e = "Predisorder raised an error: {}".format(f.read())

                _log.error(e)
                raise ServiceError(e)
        except subprocess.CalledProcessError as e:
            _log.error(e)
            raise ServiceError(e.message)
        finally:
            for path in [errlog_name, out_file, fasta_filename]:
                if os.path.isfile(path):
                    os.remove(path)

predisorder = PredisorderService(PREDISORDER)
