import logging
from kman_web.services.soap import run


logging.basicConfig()
_log = logging.getLogger(__name__)


def run_globplot(filename):
    gp_url = "http://globplot.embl.de/webservice/globplot.wsdl"

    with open(filename) as a:
        fasta = a.read()
    seq = ''.join(fasta.splitlines()[1:])
    seq_id = 'cram'
    propensity = 'Russell/Linding'

    data = run(gp_url, 400, 'runGlobPlotter', seq_id, seq, propensity)

    _log.debug('WSDL Data {}'.format(data))
    return data
