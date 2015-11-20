import re

from kmad_web.domain.features.analysis.helpers import (
    get_seq_range, group_features_positionwise)


def analyze_motifs(mutation, sequences):
    """
    :return: {
        'residues': [
            {
                'position': 1,  # 1-based!
                'motifs': [{
                'motif-id': {
                             'wild': '0',
                             'mutant': '3',
                             'class': 'motif-class',
                             'probability': 0.0-1.0
                }
                # 0 - no motif, 2 - some possibility of a motif,
                # 3 - very high possibility of a motif, 4 - annotated motif
                }],
            }
        ]
    }
    """
    group_features_positionwise(sequences)
    first_seq_motifs = sequences[0]['feat_pos'][mutation.position]['motifs']
    wild_motifs = _get_wild_motifs(mutation, sequences, first_seq_motifs)
    mutant_motifs = _get_mutant_motifs(mutation, wild_motifs)
    motif_data = _process_motifs(mutation, wild_motifs, mutant_motifs)
    return motif_data


def _get_wild_motifs(mutation, sequences, first_seq_motifs):
    """
    Returns motifs that appear in the first sequence and are conserved
    in the alignment within a (-10,+10) range form the mutation site
    OR are annotated at the mutation site (probability == 1)

    :return: motif instances of motif classes that are conserved
    """
    threshold = 0.5
    aln_length = len(sequences[0]['aligned'])
    seq_N = len(sequences)
    start = mutation.alignment_position - 10
    end = mutation.alignment_position + 10
    if start < 10:
        start = 0
    if end > aln_length - 1:
        end = aln_length
    # create motif_count dict: keys are motif_ids of the motifs on
    # mutation site
    motif_count = _count_motifs(first_seq_motifs, sequences, start,
                                end)
    wild = []
    for m in first_seq_motifs:
        if (float(motif_count[m['id']]) / seq_N >= threshold
                or m['probability'] == 1):
            wild.append(m)
    return wild


def _count_motifs(first_seq_motifs, sequences, start, end):
    motif_count = {m['id']: 1 for m in first_seq_motifs}
    # first count motifs
    for s in sequences[1:]:
        # set of motifs in the ith sequence within the +10 - -10 range
        sequence_motifs = set()
        seq_range = get_seq_range(s['aligned'], start, end)
        seq_start = seq_range['start']
        seq_end = seq_range['end']
        if seq_start is not None:
            for p in s['feat_pos'][seq_start:seq_end]:
                for m in p['motifs']:
                    if m['id'] in motif_count.keys():
                        sequence_motifs.add(m['id'])
        for m_id in sequence_motifs:
            motif_count[m_id] += 1
    return motif_count


def _get_mutant_motifs(mutation, conserved_motifs):
    """
    get motifs the conserved first seq motif instances that are also
    present in the mutant sequence
    """
    mutant_motifs = []
    for m in conserved_motifs:
        reg = re.compile(m['pattern'])
        seq_excerpt = mutation.mutant_sequence[m['start'] - 1:m['end']]
        if reg.match(seq_excerpt):
            mutant_motifs.append(m)
    return mutant_motifs


def _process_motifs(mutation, wild_motifs, mutant_motifs):
    motif_data = {
        'position': mutation.position + 1,
        'motifs': {}
    }
    for m in wild_motifs:
        status_wild = '4' if m['probability'] == 1 else '2'
        if m in mutant_motifs:
            status_mutant = status_wild
        else:
            status_mutant = '0'
        motif_data['motifs'][m['id']] = {
            'wild': status_wild,
            'mutant': status_mutant,
            'probability': m['probability'],
            'class': m['class']
        }
    return motif_data
