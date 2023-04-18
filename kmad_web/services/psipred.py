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
            _log.debug("calling PSIPRED: {}".format(' '.join(args)))
            with open(errlog_name, 'w') as err:
                subprocess.call(args, stderr=err)

            if os.path.exists(out_file):
                with open(out_file) as a:
                    data = a.read()
                return data
            else:
                e = ("Didn't get the output file from PSIPRED: {}\n"
                     "Submitted sequence: {}".format(
                         out_file, fasta_sequence))
                empty_errlog = os.stat(errlog_name).st_size == 0
                if not empty_errlog:
                    with open(errlog_name, 'r') as f:
                        e = "PSIPRED raised an error: {}".format(
                            f.read())
                    _log.error(e)
                    raise ServiceError(e)
                _log.error(e)
                raise ServiceError(e)

        except subprocess.CalledProcessError as e:
            _log.error(e)
            raise ServiceError(e)
        finally:
            for path in [errlog_name, fasta_filename]:
                if os.path.isfile(path):
                    os.remove(path)

            if os.path.exists(out_file):
                self.cleanup(out_file)

    def cleanup(self, out_file):
        os.remove(out_file)
        ss_file = out_file[:-1]
        horiz_file = out_file[:-3] + 'horiz'
        if os.path.exists(ss_file):
            os.remove(ss_file)
        if os.path.exists(horiz_file):
            os.remove(horiz_file)

psipred = PsipredService(PSIPRED)
