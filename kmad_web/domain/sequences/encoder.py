import logging
import string

from collections import OrderedDict

_log = logging.getLogger(__name__)
PTM_CODE_DICT = OrderedDict([
    ('phosphorylation', ["N", "O", "P", "Q", "d"]),
    ('acetylation', ["B", "C", "D", "E"]),
    ('N-glycosylation', ["F", "G", "H", "I"]),
    ('amidation', ["J", "K", "L", "M"]),
    ('hydroxylation', ["R", "S", "T", "U"]),
    ('methylation', ["V", "W", "X", "Y"]),
    ('O-glycosylation', ["Z", "a", "b", "c"])
])


class SequencesEncoder(object):
    """
    Converts sequences and annotation data to the fles format
    """
    def __init__(self):
        self._sequences = []
        self.motif_code_dict = {}
        self.motif_prob_dict = {}
        self.domain_code_dict = {}
        # domain code is 2 chars long
        self._domain_pos = 2
        # ptm code is 1 chars long
        self._ptm_pos = 4
        # motif code is 2 chars long
        self._motif_pos = 5
        self._strct_pos = 1
        self._create_code_alphabet()

    def encode(self, sequences, aligned_mode=False, use_pfam=True, use_sstrct=True):
        _log.info("Encoding sequences")
        self._sequences = sequences
        self._create_codon_sequences()
        # make code dicts for motifs and domains
        # (code dict for PTMs is constant)
        self.motif_code_dict = self._create_motif_code_dict()
        self.motif_prob_dict = self._create_motif_prob_dict()
        if use_pfam:
            self.domain_code_dict = self._create_domain_code_dict()
            self._encode_domains()
        else:
            self.domain_code_dict = {}
        # all feature positions are 1-based!
        self._encode_ptms()
        self._encode_motifs()
        if use_sstrct:
            self._encode_structure()
        self._create_encoded_sequences()
        if aligned_mode:
            self._create_encoded_aligned_sequences()

    def _create_code_alphabet(self):
        self._code_alphabet = []
        alphanum_chars = string.printable[:62]
        assert alphanum_chars.isalnum()
        alphanum_chars = list(alphanum_chars)
        # A means there is no feature - therefore it is not used in feature
        # codes
        alphanum_chars.remove('A')
        for char_i in alphanum_chars:
            for char_j in alphanum_chars:
                self._code_alphabet.append(char_i + char_j)

    def _create_motif_code_dict(self):
        feat_ids = set()
        for s in self._sequences:
            feat_ids.update([f['id'] for f in s['motifs_filtered']])
        feat_ids = list(feat_ids)
        feat_code_dict = {feat_ids[i]: self._code_alphabet[i]
                          for i in range(len(feat_ids))}
        return feat_code_dict

    def _create_domain_code_dict(self):
        feat_ids = set()
        for s in self._sequences:
            feat_ids.update([f['accession'] for f in s['domains']])
        feat_ids = list(feat_ids)
        feat_code_dict = {feat_ids[i]: self._code_alphabet[i]
                          for i in range(len(feat_ids))}
        return feat_code_dict

    def _create_encoded_sequences(self):
        for s in self._sequences:
            s['encoded_seq'] = ''.join([''.join(c) for c in s['codon_seq']])

    def _create_encoded_aligned_sequences(self):
        codon_length = 7
        for s in self._sequences:
            seq = ""
            it = 0
            for r in s['aligned']:
                if r != '-':
                    seq += s['encoded_seq'][it:it + codon_length]
                    it += codon_length
                else:
                    # equivalent of: seq += '-AAAAAA'
                    seq += '-' + 'A' * (codon_length - 1)

            s['encoded_aligned'] = seq

    """
    Encodes ptms on the sequences[lists of codons]
    ptm positions are 1-based
    """
    def _encode_ptms(self):
        # ptm position in codon
        codon_pos = self._ptm_pos
        for s in self._sequences:
            ptms = self._filter_ptms(s['ptms'])
            for p in ptms:
                ptm_pos = p['position'] - 1
                if ptm_pos < len(s['codon_seq']) \
                        and p['name'] in PTM_CODE_DICT:
                    ptm_code = PTM_CODE_DICT[p['name']][p['annotation_level']]
                    s['codon_seq'][ptm_pos][codon_pos] = ptm_code

    """
    Only one PTM can be encoded on a given position - in case of multiple PTMs
    on one position the one with higher (highest: 0, lowest: 5) annotation
    level will be encoded. In case of a equal annotation levels the one with
    lower index in the ptm_code_dict will be encoded - so phosphorylations have
    the highest priority, then the acetylations, and so on...
    """
    def _filter_ptms(self, all_ptms):
        filtered_ptms = []
        ptms_pos_wise = self._group_ptms_by_position(all_ptms)
        for p in ptms_pos_wise.values():
            ptm = {}
            if len(p) > 1:
                ptm = self._choose_ptm_to_encode(p)
                if not ptm:
                    continue
            elif p[0]['name'] in PTM_CODE_DICT:
                ptm = p[0]
            if ptm:
                filtered_ptms.append(ptm)
        return filtered_ptms

    def _choose_ptm_to_encode(self, ptms):
        # highest level -> lowest number
        # this only returns one PTM with the highest level
        encodable_ptms = [p for p in ptms
                          if p['name'] in PTM_CODE_DICT.keys()]
        ptm = {}
        if encodable_ptms:
            highest_level = min([p['annotation_level'] for p in encodable_ptms])
            # find all PTMs with highest level and names in our code dict
            highest_level_ptms = [i for i in encodable_ptms
                                  if i['annotation_level'] == highest_level]
            if len(highest_level_ptms) > 1:
                # if there is more than one PTM with the highest level choose the
                # one with lowest index in the ptm_code_dict
                ptm = min(highest_level_ptms,
                          key=lambda x: PTM_CODE_DICT.keys().index(x['name']))
            else:
                ptm = highest_level_ptms[0]
        return ptm

    def _group_ptms_by_position(self, ptms):
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
            for m in s['motifs_filtered']:
                motif_code = self.motif_code_dict[m['id']]
                for i in range(m['start'] - 1, m['end']):
                    if i < len(s['codon_seq']):
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
                domain_code = self.domain_code_dict[d['accession']]
                for i in range(int(d['start']) - 1, int(d['end'])):
                    if i < len(s['codon_seq']):
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
            s['codon_seq'] = [[r, 'A', 'A', 'A', 'A', 'A', 'A']
                              for r in s['seq']]

    def _encode_structure(self):
        order = ['TURN', 'HELIX', 'TRANSMEM', 'STRAND', 'DISULFID']
        strct_dict = {'TURN': 'T', 'TRANSMEM': 'M', 'STRAND': 'S', 'HELIX': 'H',
                      'DISULFID': 'C'}
        pos = self._strct_pos
        for s in self._sequences:
            strct = sorted(s['secondary_structure'],
                           key=lambda x: order.index(x['name']))
            for e in strct:
                strct_code = strct_dict[e['name']]
                if 'start' in e.keys():
                    for i in range(int(e['start']) - 1, int(e['end'])):
                        if i < len(s['codon_seq']):
                            s['codon_seq'][i][pos] = strct_code
                elif 'position' in e.keys():
                    if e['position'] - 1 < len(s['codon_seq']):
                        s['codon_seq'][e['position'] - 1][pos] = strct_code

    def _create_motif_prob_dict(self):
        prob_dict = {}
        for s in self._sequences:
            for m in s['motifs_filtered']:
                if m['id'] not in prob_dict.keys() or \
                        prob_dict[m['id']] < m['probability']:
                    prob_dict[m['id']] = m['probability']
        code2prob = {}
        for m in prob_dict:
            for m_id, m_code in self.motif_code_dict.items():
                if m == m_id:
                    code2prob[m_code] = prob_dict[m]
        return code2prob
