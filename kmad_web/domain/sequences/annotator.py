from kmad_web.go.providers.uniprot import UniprotGoTermProvider
from kmad_web.identifiers.uniprot import UniprotIdProvider
from kmad_web.domain.features.providers.uniprot import UniprotFeatureProvider
from kmad_web.domain.features.providers.elm import ElmFeatureProvider
from kmad_web.domain.features.providers.pfam import PfamFeatureProvider
from kmad_web.domain.features.providers.netphos import NetphosFeatureProvider


class SequenceAnnotator(object):
    def __init__(self):
        self._sequences = []

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
        self._sequences = sequences
        self._add_missing_uniprot_ids()
        go_terms = self._get_go_terms()
        self._annotate_ptms()
        self._annotate_motifs(go_terms)
        self._annotate_domains()

    def _get_go_terms(sequences):
        uniprot = UniprotGoTermProvider()
        go_terms = set()
        for s in sequences:
            seq_go_terms = uniprot.get_go_terms(s['id'])
            go_terms.update(seq_go_terms)
        return go_terms

    def _add_missing_uniprot_ids(sequences):
        uniprot = UniprotIdProvider()
        for s in sequences:
            if not s['id']:
                uniprot.get_uniprot_id(s['seq'])

    def _annotate_ptms(sequences):
        uniprot = UniprotFeatureProvider()
        netphos = NetphosFeatureProvider()
        for s in sequences:
            s['ptms'] = netphos.get_phosphorylations(s['seq'])
            if s['id']:
                s['ptms'].extend(uniprot.get_ptms(s['id']))

    def _annotate_motifs(sequences, go_terms):
        elm = ElmFeatureProvider()
        for s in sequences:
            s['motifs'] = elm.get_motif_instances(s['seq'], s['id'])
            s['motifs_filtered'] = elm.filter_motifs(s['motifs'])

    def _annotate_domains(sequences):
        for s in sequences:
            fasta_sequence = '>seq\n{}\n'.format(s)
            pfam = PfamFeatureProvider()
            s['domains'] = pfam.get_domains(fasta_sequence)
