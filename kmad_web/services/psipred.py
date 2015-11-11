import os
import subprocess

from kmad_web.default_settings import PSIPRED
from kmad_web.services.types import ServiceError


class PsipredService(object):
    def __init__(self, path):
        self._path = path

    def __call__(self, fasta_filename):
        out_file = ('.'.join(
            fasta_filename.split('.')[:-1])+".ss2").split('/')[-1]
        args = [self._path, fasta_filename]
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

psipred = PsipredService(PSIPRED)
