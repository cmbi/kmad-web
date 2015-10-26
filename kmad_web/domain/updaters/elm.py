import json

from kmad_web.parsers.elm import ElmParser
from kmad_web.services.elm import ElmService
from kmad_web.services.go import GoService
from kmad_web.domain.go.providers.go import GoProvider
from kmad_web.default_settings import ELM_URL, GO_URL, ELM_DB


class ElmUpdater(object):
    def __init__(self):
        self._elmdb_path = ELM_DB
        # hold extended go_terms (go term family = go_term + parents + all
        # descendants) in _go_families not to look twice for the same thing
        self._go_families = {}

    def update(self):
        elm_service = ElmService(ELM_URL)
        elm_parser = ElmParser(ELM_URL)
        # get raw classes data from ELM
        elm_data = elm_service.get_all_classes()
        # and parse it
        elm_parser.parse_motif_classes(elm_data)
        full_motif_classes = elm_parser.motif_classes.copy()
        for motif_id in elm_parser.motif_classes:
            extended_go_terms = self._get_extended_go_terms(motif_id)
            full_motif_classes[motif_id]['GO'] = extended_go_terms
        # write processed motif_classes to a json file
        with open(self._elmdb_path, 'w') as outfile:
            json.dumps(elm_parser.motif_classes, outfile)

    def _get_extended_go_terms(self, motif_id):
        elm_service = ElmService(ELM_URL)
        go_terms = elm_service.get_motif_go_terms(motif_id)
        for go_term in go_terms:
            if go_term not in self._go_families.keys():
                go = GoProvider()
                go.get_parent_terms(go_term)
                go.get_children_terms(go_term)
                go_family = go.parents + go.children
                self._go_families[go_term] = go_family
            else:
                go_family = go_families[go_terms]
            go_terms.extend(go_family)
        return go_terms
