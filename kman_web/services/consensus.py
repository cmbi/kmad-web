def find_consensus_disorder(odd):
    odd_list = [i[1] for i in odd]
    consensus = ["consensus", []]
    half = float(len(odd_list))/2
    for i in range(len(odd_list[0])):
        column = [odd_list[j][i] for j in range(len(odd_list))]
        if column.count(0) > half:
            consensus[1] += [0]
        elif column.count(2) > half:
            consensus[1] += [2]
        else:
            consensus[1] += [1]
    return consensus


def find_next_length(seq, pos):
    state = seq[pos]
    n_length = 1
    for i in seq[pos+1:]:
        if i == state:
            n_length += 1
        else:
            break
    return n_length


def filter_out_short_stretches(cons):
    new_cons = ["filtered", []]
    prev_length, curr_length = 0, 0
    # current state {no, maybe, yes} {0,1,2}
    prev_state, curr_state = cons[0], cons[0]
    for i in range(len(cons)):
        if cons[i] == curr_state:
            curr_length += 1
        else:
            # the end of the current state - check if it's long enough
            # if not change it to another state & add the elements form
            # the curr_state to the new_cons
            next_state = cons[i]
            if (curr_length < 4
                    and curr_length < prev_length
                    and prev_state == next_state
                    and curr_length < find_next_length(cons, i)):
                # add curr_length elements of previous(=next) state
                new_cons[1] += [prev_state for j in range(curr_length)]
            else:
                new_cons[1] += [curr_state for j in range(curr_length)]
            prev_length = curr_length
            prev_state = curr_state
            curr_state = cons[i]
            curr_length = 1
    if curr_length < 4 and curr_length < prev_length:
        new_cons[1] += [prev_state for j in range(curr_length)]
    else:
        new_cons[1] += [curr_state for j in range(curr_length)]

    return new_cons
