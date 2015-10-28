import math
import re

from kmad_web.default_settings import ELM_URL, ELMDB_PATH
from kmad_web.services.elm import ElmService
from kmad_web.parsers.elm import ElmParser


class ELmFeatureProvider(object):
    # go_terms[set] - go_terms for the full set of sequences
    def __init__(self, go_terms):
        elm_parser = ElmParser(ELMDB_PATH)
        elm_parser.parse_full_motif_classes()
        self._full_motif_classes = elm_parser.full_motif_classes.copy()
        self._process_motif_classes()
        self._go_terms = go_terms

    # uniprot_id - can be None if the sequence is not present in Uniprot -
    #              then return only predicted motifs
    # sequence - plain sequence string (not FASTA)
    def get_motif_instances(self, sequence, uniprot_id):
        motifs = []
        # parse the ELM DB
        # if uniprot_id is not None get annotated instances
        if uniprot_id:
            elm_service = ElmService(ELM_URL)
            instances = elm_service.get_instances(uniprot_id)
            elm_parser = ElmParser()
            elm_parser.parse_instances(instances)
            # combine data from the motif instances parser with data
            # from the ELM DB
            instances = self._get_more_info(elm_parser.motif_instances)
            motifs.extend(instances)
        # get predicted motifs
        instances = self._predict_motifs(sequence)
        motifs.extend(instances)
        return motifs

    def _process_motif_classes(self):
        for m in self._full_motif_classes:
            m['compiled_regex'] = re.compile(m['pattern'])
            m['GO'] = set(m['GO'])
            m['probability']

    def _predict_motifs(self, sequence):
        motifs = []
        for m_id in self._full_motif_classes:
            m = self._full_motif_classes[m_id]
            if m['GO'].intersection(self._go_terms):
                for match in m['compiled_regex'].finditer(sequence):
                    motif = {}
                    motif['start'] = match.span()[0] + 1
                    motif['end'] = match.span()[1]
                    # calc 0-1 probbaility from the ELM's e-value like
                    # probabilty
                    motif['probability'] = 1 + 1/math.log(m['probability'])
                    motif['id'] = m_id
                    motif['class'] = m['class']
                    motif['pattern'] = m['pattern']
                    motifs.append(motif)
        return motifs

    def _get_more_info(self, motif_instances):
        instances = []
        for m in motif_instances:
            m_class = self._full_motif_classes[m['id']]
            new = m.copy()
            new['probability'] = 1
            new['class'] = m_class['class']
            new['pattern'] = m_class['pattern']
            instances.append(new)
        return instances
