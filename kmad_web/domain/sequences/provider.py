from kmad_web.default_settings import UNIPROT_URL
from kmad_web.services.uniprot import UniprotService
from kmad_web.domain.sequences.fasta import parse_fasta


class UniprotSequenceProvider(object):
    def __init__(self):
        self._url = UNIPROT_URL

    def get_sequence(self, uniprot_id):
        uniprot = UniprotService(self._url)
        fasta = uniprot.get_fasta(uniprot_id)
        sequence = parse_fasta(fasta)
        return sequence
