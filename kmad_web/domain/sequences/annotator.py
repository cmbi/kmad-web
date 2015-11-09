import logging
import time

from kmad_web.domain.go.providers.uniprot import UniprotGoTermProvider
from kmad_web.domain.sequences.uniprot_id import get_uniprot_id
from kmad_web.domain.features.providers.uniprot import UniprotFeatureProvider
from kmad_web.domain.features.providers.elm import ElmFeatureProvider
from kmad_web.domain.features.providers.pfam import PfamFeatureProvider
from kmad_web.domain.features.providers.netphos import NetphosFeatureProvider


logging.basicConfig()
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
    def annotate(self, sequences):
        self.sequences = sequences
        self._add_missing_uniprot_ids()
        go_terms = self._get_go_terms()
        self._annotate_ptms()
        self._annotate_motifs(go_terms)
        self._annotate_domains()

    def _get_go_terms(self):
        uniprot = UniprotGoTermProvider()
        go_terms = set()
        for s in self.sequences:
            seq_go_terms = uniprot.get_go_terms(s['id'])
            go_terms.update(seq_go_terms)
        return go_terms

    def _add_missing_uniprot_ids(self):
        for s in self.sequences:
            if not s['id']:
                s['id'] = get_uniprot_id(s['seq'])

    def _annotate_ptms(self):
        uniprot = UniprotFeatureProvider()
        netphos = NetphosFeatureProvider()
        for s in self.sequences:
            s['ptms'] = netphos.get_phosphorylations(s['seq'])
            if s['id']:
                uniprot_ptms = uniprot.get_ptms(s['id'])
                if uniprot_ptms:
                    s['ptms'].extend(uniprot_ptms)

    def _annotate_motifs(self, go_terms):
        elm = ElmFeatureProvider(go_terms)
        for s in self.sequences:
            s['motifs'] = elm.get_motif_instances(s['seq'], s['id'])
            s['motifs_filtered'] = elm.filter_motifs(s['motifs'])

    def _annotate_domains(self):
        for s in self.sequences:
            pfam = PfamFeatureProvider()
            s['domains'] = pfam.get_domains(s)
            time.sleep(self._poll)
