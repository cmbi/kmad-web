import logging

from kmad_web.default_settings import PFAM_URL, PFAM_ID_URL
from kmad_web.parsers.pfam import PfamParser
from kmad_web.services.pfam import PfamService
from kmad_web.services.types import ServiceError


_log = logging.getLogger(__name__)


class PfamFeatureProvider(object):
    def __init__(self):
        pass

    def get_domains(self, sequence):
        fasta_sequence = ">sequence\n{}\n".format(sequence['seq'])

        domains = []
        pfam_service = PfamService(PFAM_URL, PFAM_ID_URL)
        pfam_parser = PfamParser()
        try:
            pfam_result = ""
            if sequence['id']:
                pfam_result = pfam_service.get_by_id(sequence['id'])
            if pfam_result:
                pfam_parser.parse_id_result(pfam_result)
            else:
                pfam_result = pfam_service.search(fasta_sequence)
                pfam_parser.parse(pfam_result)

            for d in pfam_parser.domains:
                domain = {}
                for key in ['accession', 'start', 'end']:
                    domain[key] = d[key]
                domains.append(domain)
        except ServiceError as e:
            _log.info("Pfam service returns an error: {},"
                      "skipping domain search for this sequence".format(
                          e.message)
                      )
        return domains
