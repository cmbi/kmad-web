import json
import logging
import time

from kmad_web.parsers.elm import ElmParser
from kmad_web.services.elm import ElmService
from kmad_web.domain.go.providers.go import GoProvider
from kmad_web.default_settings import ELM_URL, ELMDB_PATH

_log = logging.getLogger(__name__)


class ElmUpdater(object):
    def __init__(self, poll=5):
        self._poll = poll
        self._elmdb_path = ELMDB_PATH
        # hold extended go_terms (go term family = go_term + parents + all
        # descendants) in _go_families not to look twice for the same thing
        self._go_families = {}

    def update(self):
        _log.info("Running ELM update")
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
        # make json serializable
        self._make_json_friendly(full_motif_classes)
        if self._not_ok(full_motif_classes.keys()):
            raise RuntimeError("ElmUpdater: not enough motif classes")
        # write processed motif_classes to a json file
        with open(self._elmdb_path, 'w') as outfile:
            json.dump(full_motif_classes, outfile, indent=4)

    def _get_extended_go_terms(self, motif_id):
        _log.debug("Getting GO terms for the {} motif".format(motif_id))
        elm_service = ElmService(ELM_URL)
        go_terms = elm_service.get_motif_go_terms(motif_id)
        for go_term in list(go_terms):
            if go_term not in self._go_families.keys():
                _log.debug("go: {}".format(go_term))
                go = GoProvider()
                go.get_parent_terms(go_term)
                go.get_children_terms(go_term)
                _log.debug("go parents: {}".format(go.parents))
                _log.debug("go children: {}".format(go.children))
                go_family = go.parents.union(go.children)
                self._go_families[go_term] = go_family
            else:
                go_family = self._go_families[go_term]
            go_terms.update(go_family)
            time.sleep(self._poll)
        return go_terms

    def _not_ok(self, full_motif_classes):
        if len(full_motif_classes.keys()) < 200:
            return True
        else:
            return False

    # change sets to lists
    def _make_json_friendly(self, full_motif_classes):
        for m in full_motif_classes.values():
            m['GO'] = list(m['GO'])
