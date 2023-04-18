import logging
import os
import subprocess
import tempfile

from kmad_web.default_settings import SPINED, SPINED_OUTPUT_DIR
from kmad_web.services.types import ServiceError
from kmad_web.services.helpers.cache import cache_manager as cm

_log = logging.getLogger(__name__)


class SpinedService(object):
    def __init__(self, path):
        self._path = path

    @cm.cache('redis')
    def __call__(self, fasta_sequence):
        _log.info("Calling SpinedService")

        tmp_file = tempfile.NamedTemporaryFile(suffix=".fasta", delete=False)
        with tmp_file as f:
            f.write(fasta_sequence)
        fasta_filename = tmp_file.name

        tmp_name = fasta_filename.split('/')[-1].split('.')[0]
        out_file = os.path.join(SPINED_OUTPUT_DIR, tmp_name + '.spd')
        tmp_path = '/'.join(fasta_filename.split("/")[:-1])
        args = [self._path, tmp_path, tmp_name]
        errlog_name = fasta_filename + "_errlog"
        try:
            _log.debug("running spined: {}".format(' '.join(args)))
            with open(errlog_name, 'w') as err:
                subprocess.call(args, stderr=err)
            # read output file
            if os.path.exists(out_file):
                with open(out_file) as a:
                    data = a.read()
                return data
            else:
                e = "Didn't find the output file: {}".format(out_file)
                empty_errlog = os.stat(errlog_name).st_size == 0
                if not empty_errlog:
                    with open(empty_errlog, 'r') as f:
                        e = "spine-d raised an error: {}".format(
                            r.read())
                _log.error(e)
                raise ServiceError(e)
        except subprocess.CalledProcessError as e:
            _log.error(e)
            raise ServiceError(e)
        finally:
            for file_path in [fasta_filename, out_file, errlog_name]:
                if os.path.isfile(file_path):
                    os.remove(file_path)

spined = SpinedService(SPINED)
