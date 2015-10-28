from kmad_web.default_settings import UNIPROT_URL
from kmad_web.services.uniprot import UniprotService


class UniprotSequenceProvider(object):
    def __init__(self):
        self._url = UNIPROT_URL

    def get_sequence(self, uniprot_id):
        uniprot = UniprotService(self._url)
        fasta = uniprot.get_fasta(uniprot_id)
        sequence = {}
        sequence['header'] = fasta.splitlines()[0]
        sequence['seq'] = ''.join(fasta.splitlines()[1:])
        return sequence
