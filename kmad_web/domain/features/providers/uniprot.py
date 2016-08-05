import logging
from collections import OrderedDict

from kmad_web.default_settings import UNIPROT_URL
from kmad_web.services.uniprot import UniprotService
from kmad_web.domain.sequences.provider import UniprotSequenceProvider
from kmad_web.services.types import ServiceError
from kmad_web.domain.blast.provider import blast
from kmad_web.domain.features.helpers.homology import transfer_data_from_homologue
from kmad_web.parsers.uniprot import UniprotParser

_log = logging.getLogger(__name__)


class UniprotFeatureProvider(object):

    def get_ptms(self, uniprot_id):
        ptms = []
        uniprot_service = UniprotService(UNIPROT_URL)
        uniprot_parser = UniprotParser()
        uniprot_xml = uniprot_service.get_xml(uniprot_id)
        uniprot_parser.parse_ptms_xml(uniprot_xml)
        for p in uniprot_parser.ptms:
            ptm = {}
            ptm['name'] = self._get_ptm_type(p['info'])
            ptm['info'] = p['info']
            if not ptm['name']:
                ptm['name'] = ptm['info']
            ptm['position'] = int(p['position'])
            ptm['annotation_level'] = self._get_annotation_level(p['eco'])
            ptms.append(ptm)
        return ptms

    def get_secondary_structure(self, sequence):
        strct_elements = []
        if sequence['id']:
            strct_elements = self._get_secondary_structure(sequence['id'])
        else:
            closest_hit = blast.find_closest_hit(sequence['seq'])
            if closest_hit:
                result = self._get_secondary_structure(
                    closest_hit['id'])
                uniprot = UniprotSequenceProvider()
                closest_hit['seq'] = uniprot.get_sequence(closest_hit['id'])['seq']
                strct_elements = transfer_data_from_homologue(
                    sequence['seq'], closest_hit['seq'], result)
        return strct_elements

    def _get_secondary_structure(self, seq_id):
        _log.info("Getting secondary structure for id {}".format(seq_id))
        uniprot_service = UniprotService(UNIPROT_URL)
        try:
            uniprot_txt = uniprot_service.get_txt(seq_id)
            uniprot_parser = UniprotParser()
            uniprot_parser.parse_structure(uniprot_txt)
            return uniprot_parser.structure
        except ServiceError:
            return []

    def _get_annotation_level(self, eco):
        levels_dict = {
            '0000269': 0, '0000314': 0, '0000353': 0, '0000315': 0,
            '0000316': 0, '0000270': 0, '0000250': 1, '0000266': 1,
            '0000244': 1, '0000213': 2, '0000312': 1, '0000313': 2,
            '0000247': 1, '0000255': 1, '0000317': 1, '0000318': 1,
            '0000319': 1, '0000320': 1, '0000321': 1, '0000245': 1,
            '0000304': 2, '0000303': 2, '0000305': 2, '0000307': 2,
            '0000501': 3
        }
        # the first eco code is always the 'best' one ( = highest annotation
        # level), therefore taking only the first one
        lowest = 3
        for e in eco:
            if e in levels_dict.keys() and levels_dict[e] < lowest:
                lowest = levels_dict[e]
        return lowest

    def _get_ptm_type(self, ptm_info):
        types_dict = OrderedDict([
            ('Phospho', 'phosphorylation'),
            ('amide', 'amidation'),
            ('O-linked', 'O-glycosylation'),
            ('N-linked', 'N-glycosylation'),
            ('acetyl', 'acetylation'),
            ('hydroxy', 'hydroxylation'),
            ('methyl', 'methylation')
        ])
        for t in types_dict:
            if t in ptm_info:
                return types_dict[t]
