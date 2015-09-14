import logging
import os
import tempfile
import subprocess

from kmad_web import paths

from kmad_web.services.txtproc import unwrap, preprocess
from kmad_web.services.consensus import filter_out_short_stretches


logging.basicConfig()
_log = logging.getLogger(__name__)


def get_predictions(fastafile):
    with open(fastafile) as a:
        infile = unwrap(a.read().splitlines())
    predictions = []
    for i in range(len(infile), 2):
        tmp_file = tempfile.NamedTemporaryFile(suffix=".fasta", delete=False)
        _log.debug("Created tmp file '{}'".format(tmp_file.name))
        with tmp_file as f:
            _log.debug("Writing data to '{}'".format(tmp_file.name))
            f.write('\n'.join(infile[i:i+2]))
        method = os.path.join(paths.IUPRED_DIR, 'iupred')
        args = [method, fastafile, 'long']
        env = {"IUPred_PATH": paths.IUPRED_DIR}
        try:
            data = subprocess.check_output(args, env=env)
        except (subprocess.CalledProcessError, OSError) as e:
            _log.error("Error: {}".format(e))
        if data:
            prediction = preprocess(data, 'iupred')
            predictions.append(filter_out_short_stretches(prediction))
        else:
            predictions.append([])
    return predictions
