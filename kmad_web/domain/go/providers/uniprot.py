import logging

from kmad_web.default_settings import UNIPROT_URL
from kmad_web.services.uniprot import UniprotService
from kmad_web.parsers.uniprot import UniprotParser, valid_uniprot_id

_log = logging.getLogger(__name__)


class UniprotGoTermProvider(object):
    def get_go_terms(self, uniprot_id):
        if uniprot_id and valid_uniprot_id(uniprot_id):
            _log.debug("getting go terms for uniprot id: {}".format(uniprot_id))
            uniprot_service = UniprotService(UNIPROT_URL)
            uniprot_parser = UniprotParser()
            uniprot_txt = uniprot_service.get_txt(uniprot_id)
            uniprot_parser.parse_go_terms(uniprot_txt)
            go_term_data = uniprot_parser.go_terms
            go_terms = [g['code'] for g in go_term_data]
            return go_terms
        else:
            return []
