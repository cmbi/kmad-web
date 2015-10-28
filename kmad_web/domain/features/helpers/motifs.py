

# filter out overlapping motifs based on their probabilities -
# if two motifs are overlapping each other then discard the one with lower
# probability
def filter_motifs(motifs):
    # run _find_indexes_to_remove to reduce errors when a motifs is overlapping
    # with more than one other motif, e.g. (dashes represent motifs positions
    # relative to each other)
    #   motif A (prob. 0.7)  ----------
    #   motif B (prob. 0.7)    -----
    #   motif C (prob. 0.8)         --------
    # _find_indexes_to_remove in the first run when two motifs have equal
    # probability won't discard any of them (this will happen only in the
    # second run), so in this example
    # (assuming follwing order of comparisons: A-B, A-C, B-C)
    # first run will discard motif A, and second run won't discard any motifs
    # (remaining B and C are not overlapping)
    #
    # if we already discarded one of the motifs with equal probability
    # a possible mistake in this case would be to first discard B from the A-B
    # comparison, and then discard A from the B-C  comparison
    #
    # ideally we would run find_indexes_to_remove without discarding equal
    # probability motifs so many times until it wouldn't return any indexes to
    # remove, and only then remove the remaining overlapping motifs with equal
    # probabilities

    # TODO: make it less error prone
    remove_indexes = _find_indexes_to_remove(motifs, remove_equal=False)
    filtered_motifs = _remove_motifs(motifs, remove_indexes)
    remove_indexes = _find_indexes_to_remove(filtered_motifs, remove_equal=True)
    filtered_motifs = _remove_motifs(filtered_motifs, remove_indexes)
    return filtered_motifs


def _find_indexes_to_remove(motifs, remove_equal):
    remove_indexes = set()
    for it_i, m_i in enumerate(motifs):
        if it_i not in remove_indexes:
            for it_j, m_j in enumerate(motifs):
                if it_i != it_j and it_j not in remove_indexes:
                    # motif i starts inside the motif j
                    check = (m_i['start'] >= m_j['start']
                             and m_i['start'] <= m_j['end'])
                    # print (check, m_i, m_j, m_i['start'] >= m_j['start'],
                    #        m_i['start'] <= m_j['end'])
                    if check:
                        if m_i['probability'] > m_j['probability']:
                            remove_indexes.add(it_j)
                        elif m_i['probability'] < m_j['probability']:
                            remove_indexes.add(it_i)
                            break
                        elif remove_equal:
                            remove_indexes.add(it_i)
                            break
    return remove_indexes


def _remove_motifs(motifs, remove_indexes):
    filtered_motifs = motifs[:]
    remove_indexes = list(remove_indexes)
    remove_indexes.sort()
    remove_indexes = remove_indexes[::-1]
    for i in remove_indexes:
        del filtered_motifs[i]
    return filtered_motifs
