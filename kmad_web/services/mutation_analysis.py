import itertools
import logging


logging.basicConfig()
_log = logging.getLogger(__name__)


PTM_CODES = {'N': {'type': 'phosphorylation', 'level': 0},
             'O': {'type': 'phosphorylation', 'level': 1},
             'P': {'type': 'phosphorylation', 'level': 2},
             'Q': {'type': 'phosphorylation', 'level': 3},
             'd': {'type': 'phosphorylation', 'level': 4},
             'B': {'type': 'acetylation', 'level': 0},
             'C': {'type': 'acetylation', 'level': 1},
             'D': {'type': 'acetylation', 'level': 2},
             'E': {'type': 'acetylation', 'level': 3},
             'F': {'type': 'N-glycosylation', 'level': 0},
             'G': {'type': 'N-glycosylation', 'level': 1},
             'H': {'type': 'N-glycosylation', 'level': 2},
             'I': {'type': 'N-glycosylation', 'level': 3},
             'J': {'type': 'amidation', 'level': 0},
             'K': {'type': 'amidation', 'level': 1},
             'L': {'type': 'amidation', 'level': 2},
             'M': {'type': 'amidation', 'level': 3},
             'R': {'type': 'hydroxylation', 'level': 0},
             'S': {'type': 'hydroxylation', 'level': 1},
             'T': {'type': 'hydroxylation', 'level': 2},
             'U': {'type': 'hydroxylation', 'level': 3},
             'V': {'type': 'methylation', 'level': 0},
             'W': {'type': 'methylation', 'level': 1},
             'X': {'type': 'methylation', 'level': 2},
             'Y': {'type': 'methylation', 'level': 3},
             'Z': {'type': 'O-glycosylation', 'level': 0},
             'a': {'type': 'O-glycosylation', 'level': 1},
             'b': {'type': 'O-glycosylation', 'level': 2},
             'c': {'type': 'O-glycosylation', 'level': 3}
             }


def codon_to_features(codon, feature_codemap):
    if codon[4] in PTM_CODES.keys():
        ptm_dict = PTM_CODES[codon[4]]
    else:
        ptm_dict = {}

    if codon[5:] != 'AA':
        motif_index = feature_codemap['motifs'].index(list(
            itertools.ifilter(lambda x: x[0] == codon[5:],
                              feature_codemap['motifs']))[0])
        motif_name = feature_codemap['motifs'][motif_index][1]
        motif_regex = feature_codemap['motifs'][motif_index][2]
        motif_dict = {'name': motif_name, 'regex': motif_regex,
                      'code': codon[5:]}
    else:
        motif_dict = {}

    features = {'ptm': ptm_dict,
                'motif': motif_dict
                }
    return features


def preprocess_features(encoded_alignment, feature_codemap):
    aligned_sequences = []
    n = 7
    for i in encoded_alignment:
        if not i.startswith('>'):
            aligned_sequences.append([])
            for j in range(0, len(i), n):
                new_residue = {'aa': i[j],
                               'features': codon_to_features(i[j: j + n],
                                                             feature_codemap)}
                aligned_sequences[-1].append(new_residue)
    return aligned_sequences


def analyze_ptms(alignment, mutation_site, alignment_position, new_aa):
    level_to_score = {0: 1., 1: 0.9, 2: 0.8, 3: 0.7, 4: 0.3}
    result = {'position': mutation_site,
              'ptms': {}}
    ptm = alignment[0][alignment_position]['features']['ptm']
    threshold = 0.3
    status_wild = ''
    status_mut = 'N'
    if ptm:
        # if annotated
        if ptm['level'] < 4:
            status_wild = 'certain'
        else:
            # it is predicted, so now check if:
            # - the conservation of annotated
            # ptms is above the threshold
            # or
            # - if all four sequences (after the query seq. have an
            # annotated ptm of that type)
            conservation = 0
            first_four = True
            for i in range(1, len(alignment)):
                ptm_i = alignment[i][alignment_position]['features']['ptm']
                if ptm_i and ptm['type'] == ptm_i['type']:
                    conservation += level_to_score[ptm_i['level']]
                if i < 5 and (not ptm_i or ptm_i['level'] < 4):
                    first_four = False
            conservation = conservation / len(alignment)
            if conservation > threshold or first_four:
                status_wild = 'putative'
    if new_aa == alignment[0][alignment_position]['aa']:
        status_mut = 'Y'
    if status_wild:
        result['ptms'][ptm['type']] = [status_wild, status_mut, 'description']
    return result


def get_motif_list(alignment, encoded_alignment, wild_seq, mutation_site):
    motifs = set()
    start_pos = mutation_site - 5
    end_pos = mutation_site + 5
    if start_pos < 0:
        start_pos = 0
    if end_pos >= len(wild_seq):
        end_pos = len(wild_seq) - 1

    for i, seqI in enumerate(alignment):
        real_start = get_real_position(encoded_alignment, start_pos, i)
        real_end = get_real_position(encoded_alignment, end_pos, i)
        for j in range(real_start, real_end):
            if seqI[j]['features']['motif']:
                motifs.add(alignment[i][j]['features']['motif']['code'])
    return motifs



def analyze_motifs(alignment, raw_alignment, encoded_alignment, wild_seq,
                   mutant_seq, mutation_site, alignment_position,
                   feature_codemap):
    # 1. go through the alignment, in each sequence check all residues
    # from -5 to +5 relative to the mutation position
    # 2. get ALL the motifs annotated to these residues
    # 3. Check their conservation - not by checking if their assigned to
    # residues but by checking if the regex matches each sequence (-10 - +10)
    # 4. For every motif that:
    #       - has conservation above the threshold
    #       - matches first sequence
    #       - occurs in the 1st sequence on the mutation site
    #   check if it still matches the sequence on the same position after the
    #   mutation

    # 1.
    all_motifs = get_motif_list(alignment, encoded_alignment, wild_seq,
                                mutation_site)
    pass


def analyze_predictions(pred_phosph_wild, pred_phosph_mut, alignment,
                        mutation_site, encoded_alignment):
    result = []
    # missing - phosphorylations predicted in the wild seq, but in the mutant
    # seq
    missing = set(pred_phosph_wild).difference(set(pred_phosph_mut))
    # check if any of the missing phosph are 20 residues (or closer) upstream
    # or downstream from the mutation site
    for i in missing:
        if i < mutation_site + 20 and i > mutation_site - 20:
            real_pos = get_real_position(encoded_alignment, i, 0)
            ptm = alignment[0][real_pos]['features']['ptm']
            # check if any of the changed predictions were annotated as
            # phosphorylated
            if (ptm and ptm['type'] == 'phosphorylation' and ptm['level'] != 4):
                new_entry = {'position': i,
                             'ptms': {
                                 'phosphorylation': ['certain', 'N',
                                                     'description']
                             }
                             }
                result.append(new_entry)
        else:
            _log.debug("Prediction change more then 20 amino acids away from"
                       "the mutation site")
    return result


def combine_results(ptm_data, motif_data, surrounding_data,
                    disorder_prediction):
    output = {'residues': []}
    # dis_dict = {2: 'Y', 1: 'M', 0: 'N'}
    # disorder_txt = [dis_dict[i] for i in disorder_prediction]
    # for i in range(len(sequence)):
    #     new_entry = {'ptms': ptm_data[i], 'motifs': motif_data[i],
    #                  'disorder': disorder_txt[i]}
    #     output['residues'].append(new_entry)
    return output


def create_mutant_sequence(sequence, mutation_site, new_aa):
    new_sequence = (sequence[:mutation_site]
                    + new_aa
                    + sequence[mutation_site + 1:])
    return new_sequence


def get_real_position(encoded_alignment, mutation_site, seq_no):
    query_seq = encoded_alignment[2*seq_no + 1]
    query_seq = [query_seq[i] for i in range(0, len(query_seq), 7)]
    count = -1
    i = -1
    while i < len(query_seq) - 1 and count < mutation_site:
        i += 1
        if query_seq[i] != '-':
            count += 1
    return i
