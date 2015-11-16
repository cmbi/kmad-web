import os
import subprocess

from kmad_web.default_settings import SPINED, SPINED_OUTPUT_DIR
from kmad_web.services.types import ServiceError
from kmad_web.services.helpers.cache import cache_manager as cm


class SpinedService(object):
    def __init__(self, path):
        self._path = path

    @cm.cache('redis')
    def __call__(self, fasta_filename):
        tmp_name = fasta_filename.split('/')[-1].split('.')[0]
        out_file = os.path.join(SPINED_OUTPUT_DIR, tmp_name + '.spd')
        tmp_path = '/'.join(fasta_filename.split("/")[:-1])
        args = [self._path, tmp_path, tmp_name]
        try:
            subprocess.call(args)
            if os.path.exists(out_file):
                with open(out_file) as a:
                    data = a.read()
                return data
            else:
                raise ServiceError("Didn't find the output file: {}".format(
                    out_file))
        except subprocess.CalledProcessError as e:
            raise ServiceError(e.message)

spined = SpinedService(SPINED)
