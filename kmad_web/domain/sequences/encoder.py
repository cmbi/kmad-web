from collections import OrderedDict


class SequencesEncoder(object):
    def __init__(self):
        self._sequences = []
        self._motif_code_map = {}
        self._domain_code_map = {}
        # domain code is 2 chars long
        self._domain_pos = 2
        # ptm code is 1 chars long
        self._ptm_pos = 4
        # motif code is 2 chars long
        self._motif_pos = 5

    def encode(self, sequences):
        self._sequences = sequences
        self._create_codon_sequences()
        # make code maps for motifs and domains (code map for PTMs is constant)
        self._make_feature_code_map('motifs')
        self._make_feature_code_map('domains')
        # all feature positions are 1-based!
        self._encode_ptms()
        self._encode_motifs()
        self._encode_domains()
        self._create_encoded_sequences()

    def _create_encoded_sequences(self):
        for s in self._sequences:
            s['encoded_seq'] = ''.join([''.join(c) for c in s['codon_seq']])

    """
    Encodes ptms on the sequences[lists of codons]
    ptm positions are 1-based

    Only one PTM can be encoded on a given position - in case of multiple PTMs
    on one position the one with higher (highest: 0, lowest: 5) annotation
    level will be encoded. In case of a equal annotation levels the one with
    lower index in the ptm_code_map will be encoded - so phosphorylations have
    the highest priority, then the acetylations, and so on...
    """
    def _encode_ptms(self):
        ptm_code_map = OrderedDict([
            ('phosphorylation', ["N", "O", "P", "Q", "d"]),
            ('acetylation',     ["B", "C", "D", "E"]),
            ('N-glycosylation', ["F", "G", "H", "I"]),
            ('amidation',       ["J", "K", "L", "M"]),
            ('hydroxylation',   ["R", "S", "T", "U"]),
            ('methylation',     ["V", "W", "X", "Y"]),
            ('O-glycosylation', ["Z", "a", "b", "c"])
        ])
        # position in codon
        pos = self._ptm_pos
        for s in self._sequences:
            ptms = self._filter_ptms(s['ptms'])
            for p in ptms:
                ptm_code = ptm_code_map[p['name']][p['annotation_level']]
                s['codon_seq'][p['position']][pos] = ptm_code

    def _filter_ptms(self, all_ptms):
        filtered_ptms = []
        ptms_pos_wise = self._group_ptms_by_position(all_ptms)
        for p in ptms_pos_wise.values():
            if len(p) > 1:
                ptm = self._choose_ptm_to_encode(p)
            else:
                ptm = p[0]
            filtered_ptms.append(ptm)
        return filtered_ptms

    def _group_ptms_by_position(ptms):
        ptms_pos_wise = {}
        for p in ptms:
            if p['position'] not in ptms_pos_wise.keys():
                ptms_pos_wise[p['position']] = []
            ptms_pos_wise[p['position']].append(p)
        return ptms_pos_wise

    """
    Encodes motifs on the sequences[lists of codons]
    motif positions are 1-based
    """
    def _encode_motifs(self):
        # position in codon
        pos = self._motif_pos
        for s in self._sequences:
            for m in s['motifs']:
                motif_code = self._motif_code_map[m['id']]
                for i in range(m['start'] - 1, m['end']):
                    s['codon_seq'][i][pos:pos+2] = motif_code

    """
    Encodes domains on the sequences[lists of codons]
    domain positions are 1-based
    """
    def _encode_domains(self):
        # position in codon
        pos = self._domain_pos
        for s in self._sequences:
            for d in s['domains']:
                domain_code = self._domain_code_map[d['accession']]
                for i in range(d['start'] - 1, d['end']):
                    s['codon_seq'][i][pos:pos+2] = domain_code

    """
    From each string sequences it creates a codon sequence, e.g.
    for sequence 'SEQ' the codon sequence will be:
        [
         ['S', 'A', 'A', 'A', 'A', 'A', 'A'],
         ['E', 'A', 'A', 'A', 'A', 'A', 'A'],
         ['Q', 'A', 'A', 'A', 'A', 'A', 'A'],
        ]
    This is only needed to easily encode features and later create encoded
    sequences
    """
    def _create_codon_sequences(self):
        for s in self._sequences:
            s['codon_seq'] = [list(s['seq'][i: i + 7])
                              for i in range(0, len(s['seq'], 7))]
