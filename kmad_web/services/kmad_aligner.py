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
    def align(self, fles_file, gop, gep, egp, ptm_score, domain_score,
              motif_score, conf_path, gapped, full_ungapped,
              refine):
        _log.info("Running KMAD alignment [service]")

        tmp_file = tempfile.NamedTemporaryFile(suffix=".fasta", delete=False)
        with tmp_file as f:
            f.write(fles_file)
        fles_path = tmp_file.name

        args = [self._path, '-i', fles_path, '-o', fles_path, '-g', gop,
                '-e', gep, '-n', egp, '-p', ptm_score, '-m', motif_score,
                '-d', domain_score, '--out-encoded', '-c', '7']
        result_path = fles_path + '_al'
        if conf_path:
            args.extend(['--conf', conf_path])
        if refine:
            args.extend(['--refine'])
        if gapped:
            args.extend(['--gapped'])
        elif full_ungapped:
            args.extend(['--full_ungapped'])

        try:
            subprocess.call(args)
        except subprocess.CalledProcessError as e:
            raise ServiceError(e)
        if os.path.exists(result_path):
            return result_path
        else:
            raise ServiceError("KMAD result not found: {}".format(result_path))

kmad = KmadAligner(KMAD)
