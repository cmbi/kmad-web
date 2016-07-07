import logging

from kmad_web.default_settings import UNIPROT_URL
from kmad_web.services.uniprot import UniprotService
from kmad_web.domain.sequences.fasta import parse_fasta

_log = logging.getLogger(__name__)


class UniprotSequenceProvider(object):
    def __init__(self):
        self._url = UNIPROT_URL

    def get_sequence(self, uniprot_id):
        _log.debug("Getting sequence for uniprot id {}".format(uniprot_id))
        uniprot = UniprotService(self._url)
        fasta = uniprot.get_fasta(uniprot_id)
        sequence = {}
        sequence['seq'] = parse_fasta(fasta)[0]
        sequence['id'] = uniprot_id
        return sequence
