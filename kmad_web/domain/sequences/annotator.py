import logging
import time

from kmad_web.domain.go.providers.uniprot import UniprotGoTermProvider
from kmad_web.domain.sequences.uniprot_id import get_uniprot_id
from kmad_web.domain.features.providers.uniprot import UniprotFeatureProvider
from kmad_web.domain.features.providers.elm import ElmFeatureProvider
from kmad_web.domain.features.providers.pfam import PfamFeatureProvider
from kmad_web.domain.features.providers.netphos import NetphosFeatureProvider


_log = logging.getLogger(__name__)


class SequencesAnnotator(object):
    def __init__(self):
        self.sequences = []
        self._poll = 5

    """
    input sequences
    sequences: [{'header': fasta_header,
                 'id': uniprot_id (can be None)
                 'seq': sequence}]
    output sequences
    sequences: [{'header': fasta_header,
                 'id': uniprot_id (can be None)
                 'seq': sequence,
                 'ptms': motif_list,
                 'domains': domain_list,
                 'ptms': ptm_list,
                }]
    """
    def annotate(self, sequences, use_pfam, use_sstrct):
        self.sequences = sequences
        _log.info("Annotating sequences")
        self._add_missing_uniprot_ids()
        go_terms = self._get_go_terms()
        self._annotate_ptms()
        self._annotate_motifs(go_terms)
        if use_pfam:
            self._annotate_domains()
        if use_sstrct:
            self._annotate_secondary_structure()

    def _get_go_terms(self):
        uniprot = UniprotGoTermProvider()
        go_terms = set()
        for s in self.sequences:
            seq_go_terms = uniprot.get_go_terms(s['id'])
            go_terms.update(seq_go_terms)
        return go_terms

    def _add_missing_uniprot_ids(self):
        for s in self.sequences:
            if 'id' not in s.keys() or not s['id']:
                s['id'] = get_uniprot_id(s['seq'])

    def _annotate_ptms(self):
        _log.info("Annotate sequences with PTMs")
        uniprot = UniprotFeatureProvider()
        netphos = NetphosFeatureProvider()
        for s in self.sequences:
            s['ptms'] = netphos.get_phosphorylations(s['seq'])
            if s['id']:
                uniprot_ptms = uniprot.get_ptms(s['id'])
                if uniprot_ptms:
                    s['ptms'].extend(uniprot_ptms)

    def _annotate_motifs(self, go_terms):
        _log.info("Annotate sequences with motifs")
        elm = ElmFeatureProvider(go_terms)
        for s in self.sequences:
            s['motifs'] = elm.get_motif_instances(s['seq'], s['id'])
            s['motifs_filtered'] = elm.filter_motifs(s['motifs'])

    def _annotate_domains(self):
        _log.info("Annotate sequences with domains")
        for s in self.sequences:
            pfam = PfamFeatureProvider()
            s['domains'] = pfam.get_domains(s)
            time.sleep(self._poll)

    def _annotate_secondary_structure(self):
        _log.info("Annotating sequences with secondary structure")
        for s in self.sequences:
            uniprot = UniprotFeatureProvider()
            s['secondary_structure'] = uniprot.get_secondary_structure(s)
