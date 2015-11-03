import logging

from kmad_web.default_settings import PFAM_URL
from kmad_web.parsers.pfam import PfamParser
from kmad_web.services.pfam import PfamService


logging.basicConfig()
_log = logging.getLogger(__name__)


class PfamFeatureProvider(object):
    def __init__(self):
        pass

    def get_domains(self, sequence):
        fasta_sequence = ">sequence\n{}\n".format(sequence['seq'])

        pfam_service = PfamService(PFAM_URL)
        pfam_result = pfam_service.search(fasta_sequence)

        pfam_parser = PfamParser()
        pfam_parser.parse(pfam_result)
        domains = []

        for d in pfam_parser._domains:
            domain = {}
            for key in ['accession', 'start', 'end']:
                domain[key] = d[key]
            domains.append(domain)
        return domains
