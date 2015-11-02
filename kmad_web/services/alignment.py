import subprocess

from kmad_web.default_settings import CLUSTALO, CLUSTALW, MAFFT, MUSCLE, TCOFFEE
from kmad_web.services.types import ServiceError


class ClustaloService(object):
    def __init__(self):
        self._path = CLUSTALO
        self._suffix = "_al"

    def align(self, filename):
        out_filename = filename + self._suffix
        args = [self._path, '-i', filename, '-o', out_filename]

        try:
            subprocess.call(args)
        except subprocess.CalledProcessError as e:
            raise ServiceError(e)

        return out_filename


class ClustalwService(object):
    def __init__(self):
        self._path = CLUSTALW

    def align(self, filename):
        out_filename = filename + self._suffix
        args = [
            self._path, '-INFILE={}'.format(filename),
            '-OUTFILE={}'.format(out_filename), '-OUTPUT=FASTA',
            '-OUTORDER=INPUT'
        ]

        try:
            subprocess.call(args)
        except subprocess.CalledProcessError as e:
            raise ServiceError(e)

        return out_filename


class MafftService(object):
    def __init__(self):
        self._path = MAFFT

    def align(self, filename):
        out_filename = filename + self._suffix
        args = ["mafft", filename]
        try:
            with open(out_filename, 'w') as out:
                subprocess.call(args, stdout=out)
        except subprocess.CalledProcessError as e:
            raise ServiceError(e)

        return out_filename


class MuscleService(object):
    def __init__(self):
        self._path = MUSCLE

    def align(self, filename):
        out_filename = filename + self._suffix

        args = [self._path, "-in", filename, "-out", out_filename]

        try:
            subprocess.call(args)
        except subprocess.CalledProcessError as e:
            raise ServiceError(e)

        return out_filename


class TcoffeeService(object):
    def __init__(self):
        self._path = TCOFFEE

    def align(self, filename):
        out_filename = filename + self._suffix

        args = [
            self._path, filename, "-output", "fasta_aln", "-outfile",
            out_filename
        ]

        try:
            subprocess.call(args)
        except subprocess.CalledProcessError as e:
            raise ServiceError(e)

        return out_filename
