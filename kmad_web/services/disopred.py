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
        with open(tmp_file.name, "w") as f:
            f.write(fasta_sequence)
        fasta_filename = tmp_file.name

        out_file = '.'.join(fasta_filename.split('.')[:-1]) + ".diso"
        args = [self._path, fasta_filename]
        errlog_name = out_file + "_errlog"
        try:
            with open(errlog_name, 'w') as err:
                subprocess.call(args, stderr=err)
            # remove error log file if it's empty, otherwise raise an error
            # empty_errlog = stat.st_size == 0
            # if empty_errlog:
            #     os.remove(errlog_name)
            #     os.remove(fasta_filename)
            # else:
            #     e = "Disopred raised an error, check logfile: {}".format(
            #         errlog_name)
            #     _log.error(e)
            #     raise ServiceError(e)
            if os.path.exists(out_file):
                with open(out_file) as a:
                    data = a.read()
                return data
            else:
                content = out_file
                if os.path.isfile(errlog_name):
                    with open(errlog_name, 'r') as err:
                        content = err.read()
                _log.error("Didn't find the output file: %s", content)
                raise ServiceError("Didn't find the output file: %s", content)
        except (subprocess.CalledProcessError, OSError) as e:
            msg = "\'{}\' raised:\n{}".format(' '.join(args), e)
            _log.error(msg)
            raise ServiceError(e)
        finally:
            if os.path.isfile(errlog_name):
                os.remove(errlog_name)
            if os.path.isfile(fasta_filename):
                os.remove(fasta_filename)
            if os.path.isfile(out_file):
                os.remove(out_file)

disopred = DisopredService(DISOPRED)
