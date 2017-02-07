import logging
import math
import re

from kmad_web.default_settings import ELM_URL, ELMDB_PATH
from kmad_web.services.elm import ElmService
from kmad_web.parsers.elm import ElmParser

_log = logging.getLogger(__name__)


class ElmFeatureProvider(object):
    # go_terms[set] - go_terms for the full set of sequences
    def __init__(self, go_terms, elmdb_path=None):
        if not elmdb_path:
            elmdb_path = ELMDB_PATH
        elm_parser = ElmParser(elmdb_path)
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
        self._add_predicted(motifs, instances)
        return motifs

    def _process_motif_classes(self):
        for m in self._full_motif_classes.values():
            m['compiled_regex'] = re.compile(m['pattern'])
            m['GO'] = set(m['GO'])

    def _predict_motifs(self, sequence):
        motifs = []
        for m_id in self._full_motif_classes:
            m = self._full_motif_classes[m_id]
            if all([m[k] for k in m]):
                if not self._go_terms or m['GO'].intersection(self._go_terms):
                    for match in m['compiled_regex'].finditer(sequence):
                        motif = {}
                        motif['start'] = match.span()[0] + 1
                        motif['end'] = match.span()[1]
                        # calc 0-1 probbaility from the ELM's e-value like
                        # probability
                        motif['probability'] = 1 + 1 / math.log(
                            float(m['probability']))
                        motif['id'] = m_id
                        motif['class'] = m['class']
                        motif['pattern'] = m['pattern']
                        motifs.append(motif)
        return motifs

    def _get_more_info(self, motif_instances):
        instances = []
        for m in motif_instances:
            if m['id'] not in self._full_motif_classes.keys():
                continue
            m_class = self._full_motif_classes[m['id']]
            new = m.copy()
            new['probability'] = 1
            new['class'] = m_class['class']
            new['pattern'] = m_class['pattern']
            instances.append(new)
        return instances

    def filter_motifs(self, motifs):
        """
        filter out overlapping motifs based on their probabilities -
        if two motifs are overlapping each other then discard the one with lower
        probability
        run _find_indexes_to_remove to reduce errors when a motifs is
        overlapping
        with more than one other motif, e.g. (dashes represent motifs positions
        relative to each other)
          motif A (prob. 0.7)  ----------
          motif B (prob. 0.7)    -----
          motif C (prob. 0.8)         --------
        _find_indexes_to_remove in the first run when two motifs have equal
        probability won't discard any of them (this will happen only in the
        second run), so in this example
        (assuming follwing order of comparisons: A-B, A-C, B-C)
        first run will discard motif A, and second run won't discard any motifs
        (remaining B and C are not overlapping)

        if we already discarded one of the motifs with equal probability
        a possible mistake in this case would be to first discard B from the A-B
        comparison, and then discard A from the B-C  comparison

        ideally we would run find_indexes_to_remove without discarding equal
        probability motifs so many times until it wouldn't return any indexes to
        remove, and only then remove the remaining overlapping motifs with equal
        probabilities
        """
        # TODO: make it less error prone

        remove_indexes = self._find_indexes_to_remove(motifs,
                                                      remove_equal=False)
        filtered_motifs = self._remove_motifs(motifs, remove_indexes)
        remove_indexes = self._find_indexes_to_remove(filtered_motifs,
                                                      remove_equal=True)
        filtered_motifs = self._remove_motifs(filtered_motifs, remove_indexes)
        return filtered_motifs

    def _find_indexes_to_remove(self, motifs, remove_equal):
        remove_indexes = set()
        for it_i, m_i in enumerate(motifs):
            if it_i not in remove_indexes:
                for it_j, m_j in enumerate(motifs):
                    if it_i != it_j and it_j not in remove_indexes:
                        # motif i starts inside the motif j
                        check = (m_i['start'] >= m_j['start'] and
                                 m_i['start'] <= m_j['end'])
                        if not check:
                            continue
                        if m_i['probability'] > m_j['probability']:
                            remove_indexes.add(it_j)
                        elif m_i['probability'] < m_j['probability']:
                            remove_indexes.add(it_i)
                            break
                        elif remove_equal:
                            remove_indexes.add(it_i)
                            break
        return remove_indexes

    def _remove_motifs(self, motifs, remove_indexes):
        filtered_motifs = motifs[:]
        remove_indexes = list(remove_indexes)
        remove_indexes.sort()
        remove_indexes = remove_indexes[::-1]
        for i in remove_indexes:
            del filtered_motifs[i]
        return filtered_motifs

    def _add_predicted(self, annotated, predicted):
        for mp in predicted:
            found = False
            for ma in annotated:
                if (ma['class'] == mp['class'] and
                        ma['start'] == mp['start'] and
                        ma['end'] == mp['end']):
                    found = True
                    break
            if not found:
                annotated.append(mp)
