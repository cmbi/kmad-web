import logging
import tempfile

from kmad_web.services.convert import run_netphos


logging.basicConfig()
_log = logging.getLogger(__name__)

def process_features(encoded_alignment):
    split_alignment = []
    # for i in encoded_alignment
    pass

def analyze_ptms(encoded_alignment, mutated_sequence, wild_seq_filename,
                 mut_seq_filename, mutation_site, new_aa):

    predicted_phosph_wild = run_netphos(wild_seq_filename)
    predicted_phosph_mutant = run_netphos(mutant_seq_filename)
    alignment = process_features(encoded_alignment)
    pass


def analyze_motifs(encoded_alignment, mutated_sequence, feature_codemap):
    pass


def process_mutation_result(ptm_data, motif_data, disorder_prediction,
                            sequence):
    output = {'residues': []}
    dis_dict = {2: 'Y', 1: 'M', 0: 'N'}
    disorder_txt = [dis_dict[i] for i in disorder_prediction]
    for i in range(len(sequence)):
        new_entry = {'ptms': ptm_data[i], 'motifs': motif_data[i],
                     'disorder': disorder_txt[i]}
        output['residues'].append(new_entry)
    return output


def create_mutant_sequence(sequence, mutation_site, new_aa):
    new_sequence = (sequence[:mutation_site]
                    + new_aa
                    + sequence[mutation_site + 1:])
    return new_sequence
