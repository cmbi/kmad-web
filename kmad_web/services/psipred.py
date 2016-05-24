import logging
import os
import subprocess
import tempfile

from kmad_web.default_settings import PSIPRED
from kmad_web.services.types import ServiceError
from kmad_web.services.helpers.cache import cache_manager as cm

_log = logging.getLogger(__name__)


class PsipredService(object):
    def __init__(self, path):
        self._path = path

    @cm.cache('redis')
    def __call__(self, fasta_sequence):
        _log.info("Calling PsipredService")

        tmp_file = tempfile.NamedTemporaryFile(suffix=".fasta", delete=False)
        with tmp_file as f:
            f.write(fasta_sequence)
        fasta_filename = tmp_file.name

        out_file = ('.'.join(
            fasta_filename.split('.')[:-1])+".ss2").split('/')[-1]
        args = [self._path, fasta_filename]
        errlog_name = out_file + "_errlog"
        try:
            with open(errlog_name, 'w') as err:
                subprocess.call(args, stderr=err)
            # remove error log file if it's empty, otherwise raise an error
            empty_errlog = os.stat(errlog_name).st_size == 0
            if empty_errlog:
                os.remove(errlog_name)
                os.remove(fasta_filename)
            else:
                e = "PSIPRED raised an error, check logfile: {}".format(
                    errlog_name)
                _log.error(e)
                raise ServiceError(e)

            if os.path.exists(out_file):
                with open(out_file) as a:
                    data = a.read()
                self.cleanup(out_file)
                return data
            else:
                _log.error("Didn't find the output file: {}\n"
                           "Submitted sequence: {}".format(
                               out_file, fasta_sequence))
                raise ServiceError("Didn't find the output file: {}".format(
                    out_file))
        except subprocess.CalledProcessError as e:
            _log.error(e.message)
            raise ServiceError(e.message)

    def cleanup(self, out_file):
        os.remove(out_file)
        ss_file = out_file[:-1]
        horiz_file = out_file[:-3] + 'horiz'
        if os.path.exists(ss_file):
            os.remove(ss_file)
        if os.path.exists(horiz_file):
            os.remove(horiz_file)

psipred = PsipredService(PSIPRED)
