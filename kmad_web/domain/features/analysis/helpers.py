import re


def group_features_positionwise(sequences):
    for s in sequences:
        s['feat_pos'] = []
        for r in range(len(s['seq'])):
            new_pos = {}
            new_pos['ptms'] = _get_ptms_from_position(r, s['ptms'])
            new_pos['motifs'] = _get_motifs_from_position(
                r, s['motifs'])
            new_pos['domains'] = _get_domains_from_position(
                r, s['domains'])
            s['feat_pos'].append(new_pos)


def _get_ptms_from_position(position, all_ptms):
    return [p for p in all_ptms if p['position'] - 1 == position]


def _get_domains_from_position(position, all_domains):
    domains = [d for d in all_domains
               if (int(d['start']) - 1 <= position
                   and int(d['end']) - 1 >= position)]
    return domains


def _get_motifs_from_position(position, all_motifs):
    motifs = [m for m in all_motifs
              if (int(m['start']) - 1 <= position
                  and int(m['end']) - 1 >= position)]
    return motifs


def get_seq_position(aligned_sequence, aln_position):
    """
    returns the index of the aln_position in the sequence, e.g.
    aligned sequence: '--A', aln_position: 2
    => position in the sequence: 0

    aln_position has to be a non-gap position
    :param aligned_sequence: aligned sequence string
    :param aln_position: position in the aligned sequence
    :return: seq_position
    """
    assert aligned_sequence[aln_position] != '-'
    trunc_aligned = aligned_sequence[:aln_position + 1]
    trunc_seq = re.sub('-', '', trunc_aligned)
    return len(trunc_seq) - 1


def _get_closest_seq_position(aligned_sequence, aln_position,
                              aln_max):
    """
    Similar to _get_seq_position only that non-gap positions are allowed -
    then the index of the closest upstream aa is returned,
    e.g.
    aligned sequence: 'A----A', aln_position: 2
    => seq_position: 1
    returns None when there are no residues upstream from the aln_position,
    e.g. aligned_sequence: 'A---' aln_position: 2

    :param aligned_sequence: aligned sequence string
    :param aln_position: position in the aligned sequence
    :return: seq_position
    """
    trunc_aligned = aligned_sequence[:aln_position + 1]
    trunc_seq_len = len(re.sub('-', '', trunc_aligned))
    if aligned_sequence[aln_position] != '-':
        closest_seq_position = trunc_seq_len - 1
    elif re.sub('-', '', aligned_sequence[aln_position:aln_max]):
        closest_seq_position = trunc_seq_len
    else:
        closest_seq_position = None
    return closest_seq_position


def get_seq_range(aln_seq, aln_start, aln_end):
    """
    For a given range in the alignment return the corresponding range in
    the sequence, eq.
    aln_seq: -AT-A; aln_start: 0, aln_end: 4
    => aln_range = (0,4) '-AT-'
    => seq_range = (0,2) 'AT'

    :param aln_seq: aligned sequence string
    :param aln_start: range start
    :param aln_end: range end
    :return: {'start': int, 'end': int}
    """
    seq_start = _get_closest_seq_position(aln_seq, aln_start, aln_end)
    seq_excerpt = re.sub('-', '', aln_seq[aln_start:aln_end])
    if seq_start is not None:
        seq_end = seq_start + len(re.sub('-', '', seq_excerpt))
    else:
        seq_end = None
    return {'start': seq_start, 'end': seq_end}
