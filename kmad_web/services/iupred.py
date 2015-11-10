import logging
import os
import tempfile
import subprocess

from kmad_web import paths

from kmad_web.helpers.txtproc import unwrap, preprocess
from kmad_web.services.consensus import filter_out_short_stretches


_log = logging.getLogger(__name__)


def get_predictions(fastafile):
    with open(fastafile) as a:
        infile = unwrap(a.read().splitlines())
    predictions = [[] for i in infile[::2]]
    for i in range(0, len(infile), 2):
        tmp_file = tempfile.NamedTemporaryFile(suffix=".fasta", delete=False)
        _log.debug("Created tmp file '{}'".format(tmp_file.name))
        with tmp_file as f:
            _log.debug("Writing data to '{}'".format(tmp_file.name))
            f.write('\n'.join(infile[i:i+2]))
        method = os.path.join(paths.IUPRED_DIR, 'iupred')
        args = [method, tmp_file.name, 'long']
        env = {"IUPred_PATH": paths.IUPRED_DIR}
        try:
            data = subprocess.check_output(args, env=env)
            if data:
                prediction = preprocess(data, 'iupred')
                predictions[i / 2] = filter_out_short_stretches(prediction)[1][1]
            else:
                _log.info("no prediction")
            _log.info("prediction: {}".format(predictions[i / 2]))
        except (subprocess.CalledProcessError, OSError) as e:
            _log.error("Error: {}".format(e))
        if os.path.exists(tmp_file.name):
            os.remove(tmp_file.name)
    return predictions
