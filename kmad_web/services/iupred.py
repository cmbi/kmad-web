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

    # @cm.cache('redis')
    def __call__(self, fasta_sequence):
        _log.info("Calling IupredService")

        tmp_file = tempfile.NamedTemporaryFile(suffix=".fasta", delete=False)
        with open(tmp_file.name, "w") as f:
            f.write(fasta_sequence)
        fasta_filename = tmp_file.name
        errlog_name = fasta_filename + "_errlog"

        args = [self._path, fasta_filename, 'long']
        env = {"IUPred_PATH": self._dir}
        try:
            _log.debug("running iupred: {}".format(' '.join(args)))
            with open(errlog_name, 'w') as err:
                data = subprocess.check_output(args, stderr=err, env=env)
            empty_errlog = os.stat(errlog_name).st_size == 0
            if not empty_errlog:
                with open(errlog_name, 'r') as f:
                    e = "IUPred raised an error: {}".format(
                        f.read())
                _log.error(e)
                raise ServiceError(e)

            self.check_output(data, fasta_sequence)
            return data
        except (subprocess.CalledProcessError, OSError) as e:
            _log.error(e)
            raise ServiceError(e)
        finally:
            for path in [errlog_name, fasta_filename]:
                if os.path.isfile(path):
                    os.remove(path)

    @staticmethod
    def check_output(data, fasta_sequence):
        if not data:
            _log.error("No prediction was returned")
            raise ServiceError("No prediction was returned")

        seq_length = len(''.join(fasta_sequence.splitlines()[1:]))
        prediction_length = len(data.splitlines()[9:])
        if seq_length != prediction_length:
            e = "IUPRED prediction length ({}) doesn't equal sequence length " \
                "({}).\nSequence: {}\nPrediction:\n{}".format(
                    seq_length, prediction_length, fasta_sequence, data)
            _log.error(e)
            raise ServiceError(e)

iupred = IupredService(IUPRED, IUPRED_DIR)
