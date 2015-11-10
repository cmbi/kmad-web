import re

from collections import OrderedDict

from kmad_web.default_settings import UNIPROT_URL
from kmad_web.services.uniprot import UniprotService
from kmad_web.parsers.uniprot import UniprotParser


class UniprotFeatureProvider(object):

    def get_ptms(self, uniprot_id):
        ptms = []
        uniprot_service = UniprotService(UNIPROT_URL)
        uniprot_txt = uniprot_service.get_txt(uniprot_id)
        uniprot_parser = UniprotParser()
        uniprot_parser.parse_ptms(uniprot_txt)
        for p in uniprot_parser.ptms:
            ptm = {}
            ptm['name'] = self._get_ptm_type(p['info'])
            if ptm['name']:
                ptm['position'] = int(p['position'])
                ptm['annotation_level'] = self._get_annotation_level(p['eco'])
                ptms.append(ptm)
        return ptms

    def _get_annotation_level(self, eco):
        # the first eco code is always the 'best' one ( = highest annotation
        # level), therefore taking only the first one
        eco_code = eco[0]
        levels_dict = {'0000269': 0, '0000314': 0, '0000353': 0, '0000315': 0,
                       '0000316': 0, '0000270': 0, '0000250': 1, '0000266': 1,
                       '0000247': 1, '0000255': 1, '0000317': 1, '0000318': 1,
                       '0000319': 1, '0000320': 1, '0000321': 1, '0000245': 1,
                       '0000304': 2, '0000303': 2, '0000305': 2, '0000307': 2,
                       '0000501': 3}
        return levels_dict[eco_code]

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
