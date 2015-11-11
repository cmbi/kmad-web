import subprocess

from kmad_web.default_settings import CLUSTALO, CLUSTALW, MAFFT, MUSCLE, TCOFFEE
from kmad_web.services.types import ServiceError
from kmad_web.services.helpers.cache import cache_manager as cm


class ClustaloService(object):
    def __init__(self):
        self._path = CLUSTALO
        self._suffix = "_al"

    @cm.cache('redis')
    def align(self, filename):
        out_filename = filename + self._suffix
        args = [self._path, '-i', filename, '-o', out_filename]

        try:
            subprocess.call(args, stderr=subprocess.PIPE)
        except (subprocess.CalledProcessError, OSError) as e:
            raise ServiceError(e)

        return out_filename


class ClustalwService(object):
    def __init__(self):
        self._path = CLUSTALW
        self._suffix = "_al"

    @cm.cache('redis')
    def align(self, filename):
        out_filename = filename + self._suffix
        args = [
            self._path, '-INFILE={}'.format(filename),
            '-OUTFILE={}'.format(out_filename), '-OUTPUT=FASTA',
            '-OUTORDER=INPUT'
        ]

        try:
            subprocess.call(args, stderr=subprocess.PIPE,
                            stdout=subprocess.PIPE)
        except (subprocess.CalledProcessError, OSError) as e:
            raise ServiceError(e)

        return out_filename


class MafftService(object):
    def __init__(self):
        self._path = MAFFT
        self._suffix = "_al"

    @cm.cache('redis')
    def align(self, filename):
        out_filename = filename + self._suffix
        args = [self._path, filename]
        try:
            with open(out_filename, 'w') as out:
                subprocess.call(args, stdout=out, stderr=subprocess.PIPE)
        except (subprocess.CalledProcessError, OSError) as e:
            raise ServiceError(e)

        return out_filename


class MuscleService(object):
    def __init__(self):
        self._path = MUSCLE
        self._suffix = "_al"

    @cm.cache('redis')
    def align(self, filename):
        out_filename = filename + self._suffix

        args = [self._path, "-in", filename, "-out", out_filename]

        try:
            subprocess.call(args, stderr=subprocess.PIPE,
                            stdout=subprocess.PIPE)
        except (subprocess.CalledProcessError, OSError) as e:
            raise ServiceError(e)

        return out_filename


class TcoffeeService(object):
    def __init__(self):
        self._path = TCOFFEE
        self._suffix = "_al"

    @cm.cache('redis')
    def align(self, filename):
        out_filename = filename + self._suffix

        args = [
            self._path, filename, "-output", "fasta_aln", "-outfile",
            out_filename
        ]

        try:
            subprocess.call(args, stderr=subprocess.PIPE,
                            stdout=subprocess.PIPE)
        except (subprocess.CalledProcessError, OSError) as e:
            raise ServiceError(e)

        return out_filename
