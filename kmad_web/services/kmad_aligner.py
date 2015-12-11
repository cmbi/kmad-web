import logging
import os
import subprocess
import tempfile

from kmad_web.services.types import ServiceError
from kmad_web.default_settings import KMAD
from kmad_web.services.helpers.cache import cache_manager as cm


_log = logging.getLogger(__name__)


class KmadAligner(object):
    def __init__(self, path):
        self._path = path

    @cm.cache('redis')
    def align(self, infile, gop, gep, egp, ptm_score, domain_score,
              motif_score, conf_path, gapped, full_ungapped,
              refine, codon_length='7'):
        _log.info("Running KMAD alignment [service]")

        tmp_file = tempfile.NamedTemporaryFile(suffix=".fasta", delete=False)
        with tmp_file as f:
            f.write(infile)
        inpath = tmp_file.name

        args = [self._path, '-i', inpath, '-o', inpath, '-g', gop,
                '-e', gep, '-n', egp, '-p', ptm_score, '-m', motif_score,
                '-d', domain_score, '--out-encoded', '-c', codon_length]
        result_path = inpath + '_al'
        if conf_path:
            args.extend(['--conf', conf_path])
        if refine:
            args.extend(['--refine'])
        if gapped:
            args.extend(['--gapped'])
        elif full_ungapped:
            args.extend(['--full_ungapped'])

        try:
            _log.debug("Calling KMAD with command {}".format(
                subprocess.list2cmdline(args)))
            subprocess.call(args, stderr=subprocess.PIPE)
            print "result path: {}".format(os.path.exists(result_path))
            if not os.path.exists(result_path):
                raise ServiceError(
                    "Couldn't find the alignment file: {}".format(result_path)
                )
            with open(result_path) as a:
                result_file = a.read()
            # clean up
            # os.remove(tmp_file.name)
            os.remove(result_path)
            return result_file
        except subprocess.CalledProcessError as e:
            _log.error("KMAD returned an error: {}".format(e))
            raise ServiceError(e)
        else:
            _log.error("KMAD result not found: {}".format(result_path))
            raise ServiceError("KMAD result not found: {}".format(result_path))

kmad = KmadAligner(KMAD)
