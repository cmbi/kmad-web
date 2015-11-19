import re

from kmad_web.domain.sequences.align import align_pairwise


def transfer_data_from_homologue(sequence1, sequence2, features):
    sequences = align_pairwise(sequence1, sequence2)
    position_map = _get_equivalent_positions(
        sequences[0]['aligned'], sequences[1]['aligned'])
    seq1_features = _transfer_features_from_homologue(features, position_map)
    return seq1_features


def _get_equivalent_positions(aln_sequence1, aln_sequence2):
    position_map = {}

    for i, res_i in enumerate(aln_sequence2):
        if res_i != '-' and aln_sequence1[i] == res_i:
            pos1 = _get_seq_position(aln_sequence1, i)
            pos2 = _get_seq_position(aln_sequence2, i)
            position_map[pos2] = pos1
    return position_map


def _get_seq_position(aln_sequence, aln_pos):
    seq_part = re.sub('-', '', aln_sequence[:aln_pos + 1])
    return len(seq_part) - 1


def _transfer_features_from_homologue(features, position_map):
    new_features = []
    for f in features:
        # subtract 1 to get 0-based range
        if 'start' in f.keys():
            frange = range(f['start'] - 1, f['end'])
            mapped_positions = [i for i in frange if i in position_map.keys()]
            if len(mapped_positions) > 0.8 * len(frange):
                feature = f.copy()
                # +1 to get back to the 1-based range
                feature['start'] = min(mapped_positions) + 1
                feature['end'] = max(mapped_positions) + 1
                new_features.append(feature)
        elif 'position' in f.keys() and f['position'] in position_map.keys():
            feature = f.copy()
            feature['postion'] = position_map[f['position']]
            new_features.append(feature)
    return new_features
