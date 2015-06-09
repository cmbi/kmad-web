import logging
import re


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

PTMS = ['phosphorylation', 'acetylation', 'N-glycosylation', 'amidation',
        'hydroxylation', 'methylation', 'O-glycosylation']


def codon_to_features(codon):
    if codon[4] in PTM_CODES.keys():
        ptm_dict = PTM_CODES[codon[4]]
    else:
        ptm_dict = {}

    if codon[5:] != 'AA':
        motif_code = codon[5:]
    else:
        motif_code = ''

    features = {'ptm': ptm_dict,
                'motif': motif_code
                }
    return features


def preprocess_features(encoded_alignment):
    aligned_sequences = []
    n = 7
    for i in encoded_alignment:
        if not i.startswith('>'):
            aligned_sequences.append([])
            for j in range(0, len(i), n):
                new_residue = {'aa': i[j],
                               'features': codon_to_features(i[j: j + n])}
                aligned_sequences[-1].append(new_residue)
    return aligned_sequences


def similar_surrounding(alignment, alignment_position, ptm_type, new_res):
    ali = alignment[:]
    ali[0][alignment_position]['aa'] = new_res
    result = False
    threshold = 0.5
    k = 2
    if alignment_position > 2:
        start = alignment_position - k
    else:
        start = - alignment_position

    if alignment_position + k < len(ali[0]):
        end = alignment_position + k
    else:
        end = len(ali[0]) - 1

    for i in ali[1:]:
        ptm = i[alignment_position]['features']['ptm']
        if ptm and ptm['type'] == ptm_type:
            identities = 0
            norm = len(range(start, end + 1))
            for j in range(start, end + 1):
                if ali[0][j]['aa'] == i[j]['aa']:
                    identities += 1
            if float(identities) / norm > threshold:
                result = True
                break
    return result


# checks if any sequence (apart from the query sequence) has the 'aa' residue on
# position 'alignment_position' which is annotated with 'ptm_type' and has
# similar surrounding to the query sequence (surrounding identity > cutoff)
def check_if_annotated_aa(alignment, alignment_position, ptm_type, aa):
    result = False
    for i in alignment[1:]:
        resI = i[alignment_position]
        if (resI['aa'] == aa
                and resI['features']['ptm']
                and resI['features']['ptm']['type'] == ptm_type
                and similar_surrounding([alignment[0], i],
                                        alignment_position, ptm_type, aa)):
            result = True
            break
    return result


def count_seqs_with_feature(alignment, ptm_type):
    result = 0
    if ptm_type == 'phosphorylation':
        dont_check_level = False
    else:
        dont_check_level = True
    for seq in alignment:
        for res in seq:
            if (res['features']['ptm'] and res['features']['ptm']['type']
                    and (dont_check_level
                         or res['features']['ptm']['level'] < 4)):
                result += 1
                break
    return result


def feature_conservation(alignment, alignment_position, ptm_type):
    conservation = 0   # conservation value on the position (for all sequences)
    first_four = False  # is it present in the first four sequences
    norm = count_seqs_with_feature(alignment, ptm_type)
    # norm - number of sequences with this feature annotated
    if norm > 0:
        for i in range(0, len(alignment)):
            ptm_i = alignment[i][alignment_position]['features']['ptm']
            if (ptm_i and ptm_type == ptm_i['type']
                    and ptm_i['level'] < 4):
                conservation += 1
            if i < 5 and i > 0 and (not ptm_i or ptm_i['level'] < 4):
                first_four = False
        conservation = float(conservation) / len(alignment)
    return conservation, first_four


def analyze_ptms(alignment, mutation_site, alignment_position, new_aa,
                 predicted_phosph_mutant):
    result = {'position': mutation_site + 1,
              'ptms': {}}
    ptm = alignment[0][alignment_position]['features']['ptm']
    threshold = 0.3
    high_threshold = 0.6

    for ptm_typeI in PTMS:
        status_wild = 'N'
        status_mut = 'N'
        conservation, first_four = feature_conservation(alignment,
                                                        alignment_position,
                                                        ptm_typeI)
        surrounding_match = similar_surrounding(
            alignment, alignment_position, ptm_typeI,
            alignment[0][alignment_position]['aa'])
        # annotated_aa == True if any residue on this position is of the
        # same aa type and has the same ptm type
        # first determine wild status
        if ptm and ptm['type'] == ptm_typeI and ptm['level'] < 4:
            status_wild = 'Y'
        elif ptm_typeI != 'phosphorylation' or (ptm and ptm['level'] == 4):
            annotated_aa = check_if_annotated_aa(alignment, alignment_position,
                ptm_typeI, alignment[0][alignment_position]['aa'])
            if (annotated_aa and surrounding_match):
                if conservation >= high_threshold:
                    status_wild = 'Y'
                elif conservation >= threshold or first_four:
                    status_wild = 'M'
        # now determine mutant status
        if (check_if_annotated_aa(alignment, alignment_position, ptm_typeI,
                                  new_aa)
                and similar_surrounding(alignment, alignment_position,
                                        ptm_typeI, new_aa)
                and (ptm_typeI != 'phosphorylation'
                     or mutation_site in predicted_phosph_mutant)):
            if status_wild in ['Y', 'M']:
                status_mut = status_wild
            elif conservation >= high_threshold:
                status_mut = 'Y'
            elif conservation >= threshold:
                status_mut = 'M'
        if status_wild != 'N' or status_mut != 'N':
            result['ptms'][ptm_typeI] = [status_wild, status_mut,
                                         'description']
    return result


def get_motif_list(alignment, encoded_alignment, wild_seq, mutation_site):
    motifs = set()
    start_pos = mutation_site - 5
    end_pos = mutation_site + 5
    if start_pos < 0:
        start_pos = 0
    if end_pos >= len(wild_seq):
        end_pos = len(wild_seq) - 1
    real_start = get_real_position(encoded_alignment, start_pos, 0)
    real_end = get_real_position(encoded_alignment, end_pos, 0)
    for i, seqI in enumerate(alignment):
        for j in range(real_start, real_end + 1):
            if seqI[j]['features']['motif']:
                motifs.add(alignment[i][j]['features']['motif'])
    return motifs


def filter_motifs_by_conservation(proc_alignment, all_motifs, motif_dict,
                                  alignment_position):
    filtered = []
    threshold = 0.5
    N = len(proc_alignment)
    start = alignment_position - 10
    end = alignment_position + 10
    if start < 10:
        start = 0
    if end > len(proc_alignment[1]) - 1:
        end = len(proc_alignment[1])

    for i in all_motifs:
        regex = motif_dict[i]['regex']
        count = 0
        for j in proc_alignment:
            ungapped_segment = re.sub('-', '', j[1][start:end + 1])
            match = re.search(regex, ungapped_segment)
            if match:
                count += 1
        if float(count) / N >= threshold:
            filtered.append(i)
    return filtered


def process_codemap(feature_codemap):
    result = dict()
    for i in feature_codemap['motifs']:
        result[i[0]] = {'name': i[1], 'regex': i[2]}
    return result


def get_wild_and_mut_motifs(conserved_motifs, wild_seq, mut_seq, motif_dict,
                            mutation_site, certain):
    result = {}
    for i in conserved_motifs:
        pattern = motif_dict[i]['regex']
        p = re.compile(pattern)
        matches = re.finditer(pattern, wild_seq)
        matches = [j.span() for j in list(matches)]
        for j in matches:
            if mutation_site in range(j[0] + 1, j[1] + 1):
                mutant = False
                annotated = False
                if p.match(mut_seq[j[0]:j[1]]):
                    mutant = True
                if i in certain.keys():
                    annotated = True
                result[i] = {'annotated': annotated, 'mut': mutant}
        if not matches and i in certain.keys():
            annotated = True
            mutant = False
            result[i] = {'annotated': annotated, 'mut': mutant}
    for i in certain:
        if i not in result.keys():
            start = certain[i]['coords'][0]
            end = certain[i]['coords'][1]
            mutant = False
            pattern = certain[i]['regex']
            p = re.compile(pattern)
            if p.match(mut_seq[start:end]):
                mutant = True
            result[i] = {'annotated': True, 'mut': mutant}
    return result


def process_motifs(seq_motifs, motif_dict, mutation_site):
    result = {'position': mutation_site + 1,
              'motifs': {}}
    mut_dict = {True: 'Y', False: 'N'}
    wild_dict = {True: 'Y', False: 'M'}
    for i in seq_motifs:
        status_mutant = mut_dict[seq_motifs[i]['mut']]
        status_wild = wild_dict[seq_motifs[i]['annotated']]
        motif_name = motif_dict[i]['name']
        result['motifs'][motif_name] = [status_wild, status_mutant,
                                        'description']
    return result


def process_annotated(annotated_motifs, motif_dict):
    result = {}
    for i in range(len(annotated_motifs[0])):
        name = annotated_motifs[1][i]
        coords = annotated_motifs[0][i]
        code = ''
        for j in motif_dict:
            if motif_dict[j]['name'] == name:
                code = j
                break
        regex = motif_dict[code]['regex']
        # code = motif_dict[code]['name']
        result[code] = {'name': name, 'coords': coords, 'regex': regex}
    return result


def analyze_motifs(alignment, proc_alignment, encoded_alignment, wild_seq,
                   mutant_seq, mutation_site, alignment_position,
                   feature_codemap, annotated_motifs):
    motif_dict = process_codemap(feature_codemap)
    annotated_coords = process_annotated(annotated_motifs, motif_dict)
    # find all motifs that appear in the alignment +5 and -5 residues from the
    # mutation site
    all_motifs = get_motif_list(alignment, encoded_alignment, wild_seq,
                                mutation_site)
    # find which motifs are conserved +10 and -10 residues from the mutations
    conserved_motifs = filter_motifs_by_conservation(proc_alignment, all_motifs,
                                                     motif_dict,
                                                     alignment_position)

    # check which of the conserved motifs appear in the first sequence on the
    # mutation site and check if they are still there after the mutation
    conserved_motifs = get_wild_and_mut_motifs(conserved_motifs, wild_seq,
                                               mutant_seq, motif_dict,
                                               mutation_site, annotated_coords)
    # process motifs return motifs in the final output format
    final = process_motifs(conserved_motifs, motif_dict, mutation_site)
    return final


def analyze_predictions(pred_phosph_wild, pred_phosph_mut, alignment,
                        mutation_site, encoded_alignment):
    result = []
    # missing - phosphorylations predicted in the wild seq, but in the mutant
    # seq
    #  1-BASED!!! #
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
                                 'phosphorylation': ['Y', 'N',
                                                     'description']
                             }
                             }
                result.append(new_entry)
        else:
            _log.debug("Prediction change more then 20 amino acids away from"
                       "the mutation site")
    return result


def combine_results(ptm_data, motif_data, surrounding_data,
                    disorder_prediction, mutation_site, sequence):

    dis_dict = {2: 'Y', 1: 'M', 0: 'N'}
    disorder_txt = [dis_dict[i] for i in disorder_prediction]
    output = {'residues': []}
    for i in xrange(len(sequence)):
        if (i != mutation_site - 1
                and i + 1 not in [j['position'] for j in surrounding_data]):
            output['residues'].append({'position': i + 1,
                                       'ptm': {},
                                       'motifs': {},
                                       'disordered': disorder_txt[i]})
        elif i == mutation_site:
            output['residues'].append({'position': mutation_site + 1,
                                       'ptm': ptm_data['ptms'],
                                       'motifs': motif_data['motifs'],
                                       'disordered':
                                           disorder_txt[mutation_site - 1]})
        else:
            new_residue = {'position': i + 1}
            for j in surrounding_data:
                if j['position'] == i + 1:
                    new_residue = j
                    break
            new_residue['disordered'] = disorder_txt[i]
            output['residues'].append(new_residue)

    return output


def create_mutant_sequence(sequence, mutation_site, new_aa):
    new_sequence = (sequence[:mutation_site]
                    + new_aa
                    + sequence[mutation_site + 1:])
    return new_sequence


# takes 0-based position in the sequence; returns 0-based position in the
# alignment
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
