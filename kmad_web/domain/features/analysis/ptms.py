from kmad_web.domain.features.analysis.helpers import (
    group_features_positionwise, get_seq_position)
from kmad_web.domain.features.providers.netphos import NetphosFeatureProvider

PTM_NAMES = [
    'phosphorylation', 'acetylation', 'N-glycosylation', 'amidation',
    'hydroxylation', 'methylation', 'O-glycosylation'
]


def analyze_ptms(mutation, sequences):
    """
    :return: {
        'residues': [
            {
                'position': 1,  # 1-based!
                'ptms': {
                'phosphorylation': {'wild': '0', 'mutant': '3'}
                # 0 - no PTM, 2 - some possibility of a PTM,
                # 3 - very high possibility of a PTM, 4 - annotated PTM
                },
            }
        ]
    }
    """
    group_features_positionwise(sequences)
    # compare if the PTM predictions for the wild and mutant sequences
    # differ in the surrounding of the mutation site
    prediction = _compare_phosph_predictions(mutation)
    # analyze predicted phosphorylations in context of the alignment
    surrounding_phosphorylations = _analyze_predicted_phosph(
        mutation, sequences, prediction['differences'])
    ptms = _analyze_annotated_ptms(mutation, sequences, prediction['wild'],
                                   prediction['mutant'])
    ptm_data = {'residues': surrounding_phosphorylations + [ptms]}
    return ptm_data


def _compare_phosph_predictions(mutation):
    """
    Finds predictions that are found in the wild type but not in mutant

    :return: list of positions
    """
    netphos = NetphosFeatureProvider()
    wild_phosph = netphos.get_phosphorylations(mutation.wild_sequence)
    mutant_phosph = netphos.get_phosphorylations(mutation.mutant_sequence)

    wild_p_pos = set([p['position'] - 1 for p in wild_phosph])
    mutant_p_pos = set([p['position'] - 1 for p in mutant_phosph])

    missing = wild_p_pos.difference(mutant_p_pos)
    return {'wild': wild_p_pos, 'mutant': mutant_p_pos,
            'differences': missing}


def _analyze_predicted_phosph(mutation, sequences, missing_predictions):
    """
    checks if any of the changed phosphorylation predictions
    are annotated as phosphorylated (excluding the residue on the
    mutation site - if it a phosphorylated residue is mutated we decide
    that the phosphorylation is gone, no matter the prediction)
    """
    changes = []
    for p in missing_predictions:
        if (p < mutation.position + 20 and p > mutation.position - 20
                and p != mutation.position):
            # check if there is a phosphorylation annotated on this
            # position
            ptms = sequences[0]['feat_pos'][p]['ptms']
            for ptm in ptms:
                if (ptm['name'] == 'phosphorylation'
                        and ptm['annotation_level'] != 4):
                    changed_phosph = {
                        'position': p + 1,
                        'ptms': {
                            'phosphorylation': {
                                'wild': '4',
                                'mutant': '0',
                            }
                        }
                    }
                    changes.append(changed_phosph)
                    break
    return changes


# TODO: split it up in several functions to make it less complex
def _analyze_annotated_ptms(mutation, sequences, prediction_wild,
                            prediction_mutant):
    result = {'position': mutation.position + 1,
              'ptms': {}}
    for ptm_name in PTM_NAMES:
        status_wild = '0'
        status_mutant = '0'
        high_threshold = 0.6
        low_threshold = 0.3
        conservation = _calc_ptm_conservation(
            sequences, mutation.alignment_position, ptm_name)
        # first determine wild_type status
        query_seq_ptms = sequences[0]['feat_pos'][mutation.position]['ptms']
        # check if it's annotated in the wild type
        for p in query_seq_ptms:
            if ptm_name == p['name'] and p['annotation_level'] < 4:
                status_wild = '4'
                break
        if (status_wild == '0' and (ptm_name != 'phosphorylation'
                                    or mutation.position in prediction_wild)):
            annotated_aa = _check_if_annotated_aa(
                mutation, sequences, ptm_name,
                sequences[0]['seq'][mutation.position])
            if (annotated_aa
                and (conservation['all'] >= high_threshold
                     or conservation['first_four'])):
                status_wild = '3'
            elif annotated_aa and conservation['all'] >= low_threshold:
                status_wild = '2'
        # determine mutant status
        annotated_aa = _check_if_annotated_aa(
            mutation, sequences, ptm_name, mutation.mutant_aa)
        if (annotated_aa and (ptm_name != 'phosphorylation'
                              or mutation.position in prediction_mutant)):
            if status_wild in ['2', '3', '4']:
                status_mutant = status_wild
            elif (conservation['all'] >= high_threshold
                  or conservation['first_four']):
                status_mutant = '3'
            elif conservation['all'] >= low_threshold:
                status_mutant = '2'
        if status_wild != '0' or status_mutant != '0':
            result['ptms'][ptm_name] = {
                'wild': status_wild,
                'mutant': status_mutant
            }
    return result


def _check_if_annotated_aa(mutation, sequences, ptm_name, aa):
    """
    checks if any sequence (apart from the query sequence) has the 'aa'
    residue on
    position 'alignment_position' which is annotated with 'ptm_type' and has
    similar surrounding to the query sequence
    (surrounding identity > cutoff)

    """
    result = False
    for s in sequences[1:]:
        if s['aligned'][mutation.alignment_position] == aa:
            # check if there is any sequence with this ptm annotated
            # that has high local similarity to our sequence
            locally_similar = _check_local_similarity(
                mutation, sequences[0]['aligned'], s['aligned'])
            if s['aligned'][mutation.alignment_position] != '-':
                pos = get_seq_position(s['aligned'],
                                       mutation.alignment_position)
                ptms = s['feat_pos'][pos]['ptms']
                ptm_found = False
                for p in ptms:
                    if p['name'] == ptm_name:
                        ptm_found = True
                        break
                if ptm_found and locally_similar:
                    result = True
                    break
    return result


def _check_local_similarity(mutation, sequence1, sequence2):
    result = False
    threshold = 0.5
    k = 2
    aln_length = len(sequence1)
    if mutation.alignment_position > 2:
        start = mutation.alignment_position - k
    else:
        start = - mutation.alignment_position

    if mutation.alignment_position + k < aln_length:
        end = mutation.alignment_position + k
    else:
        end = aln_length - 1
    identities = 0
    norm = len(range(start, end + 1))
    for j in range(start, end + 1):
        if sequence1[j] == sequence2[j]:
            identities += 1
    if float(identities) / norm > threshold:
        result = True
    return result


def _calc_ptm_conservation(sequences, position, ptm_name):
    count = 0
    first_four = True
    for i, s in enumerate(sequences):
        if s['aligned'][position] != '-':
            pos = get_seq_position(s['aligned'], position)
            if ptm_name in [i['name'] for i in s['feat_pos'][pos]['ptms']]:
                count += 1
            elif i < 4:
                first_four = False
    conservation = float(count) / len(sequences)
    return {'all': conservation, 'first_four': first_four}
