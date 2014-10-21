import logging
import os
import tempfile

from kman_web.default_settings import *
from kman_web.services import txtproc


logging.basicConfig()
_log = logging.getLogger(__name__)


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
    prev_length, curr_length, next_length = 0, 0, 0
    curr_state = cons[0] # current state {no, maybe, yes} {0,1,2}
    for i in range(len(cons)):
        if cons[i] == curr_state:
            curr_length += 1
        else:       #the end of the current state - check if it's long enough if not change it to another state & add the elements form the curr_state to the new_cons
            next_state = cons[i]
            if curr_length < 4 and curr_length < prev_length and prev_state == next_state and curr_length < find_next_length(cons, i):
                new_cons[1] += [prev_state for j in range(curr_length)]    # add curr_length elements of previous(=next) state
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

     
def getID(seq, tmpname):
    header = seq.split("\n")[0].split("|")
    if len(header) > 1:
        seq_id = header[1]
    else: 
        seq_id = (tmpname.split("/")[-1]).split(".")[0]
    return seq_id


def get_sequence_from_spd(filename):
    spd_file = open("kman_web/results/"+filename+".spd").readlines()
    seq = [i[0] for i in spd_file]
    return ''.join(seq)
    
    
def get_results(filename):
    odd = []
    sequence = get_sequence_from_spd(filename)
    #try:
    for method_name in ["spine", "disopred", "predisorder", "psipred"]:
        out_file = filename + extension[method_name]
        out_file = "kman_web/results/"+out_file
        prediction_result = open(out_file).read()
        prediction_result = txtproc.preprocess(prediction_result, method_name)
        odd += [prediction_result]
    consensus = find_consensus_disorder(odd)
    odd += [consensus]
    odd += [filter_out_short_stretches(consensus[1])]
    #except:
    #    print "No such file"
    #finally:
    data = [sequence]
    data += odd
    return data


def run_predictions(fasta_seq):
    from kman_web import tasks
    from celery import group
    tmp_file = tempfile.NamedTemporaryFile(suffix=".fasta",delete=False)
    fasta_seq = txtproc.process_fasta(fasta_seq)
    sequence = fasta_seq.splitlines()[1]
    seq_id = getID(fasta_seq, tmp_file.name)
    _log.debug("Created tmp file '{}'".format(tmp_file.name))
    methods = ["spine", "disopred", "predisorder", "psipred"]
    try:
        with tmp_file as f:
            _log.debug("Writing data to '{}'".format(tmp_file.name))
            f.write(fasta_seq)
        _log.info("Calling prediction program")
        job = group(tasks.run_single_predictor.s(tmp_file.name, method_name, seq_id) for method_name in methods)
        result = job.apply_async()
        odd = result.get()
        consensus = find_consensus_disorder(odd)
        odd += [consensus]
        odd += [filter_out_short_stretches(consensus[1])]
    finally:
        _log.debug("Deleting tmp file '{}'".format(tmp_file.name))
        os.remove(tmp_file.name)
    return sequence, odd, seq_id
