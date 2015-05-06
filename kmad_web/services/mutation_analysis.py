import logging

from kmad_web.services.convert import run_netphos


logging.basicConfig()
_log = logging.getLogger(__name__)


PTM_CODES = {'N': "ptm_phosph0", 'O': "ptm_phosph1", 'P': "ptm_phosph2",
             'Q': "ptm_phosph3", 'd': "ptm_phosphP",
             'B': "ptm_acet0", 'C': "ptm_acet1", 'D': "ptm_acet2",
             'E': "ptm_acet3",
             'F': "ptm_Nglyc0", 'G': "ptm_Nglyc1", 'H': "ptm_Nglyc2",
             'I': "ptm_Nglyc3",
             'J': "ptm_amid0", 'K': "ptm_amid1", 'L': "ptm_amid2",
             'M': "ptm_amid3",
             'R': "ptm_hydroxy0", 'S': "ptm_hydroxy1", 'T': "ptm_hydroxy2",
             'U': "ptm_hydroxy3",
             'V': "ptm_methyl0", 'W': "ptm_methyl1", 'X': "ptm_methyl2",
             'Y': "ptm_methyl3",
             'Z': "ptm_Oglyc0", 'a': "ptm_Oglyc1", 'b': "ptm_Oglyc2",
             'c': "ptm_Oglyc3"
             }


def codon_to_features(codon):
    features = {'ptm': PTM_CODES[codon[4]],
                'motif': 'motif_{}'.format(codon[5:])}
    return features


def process_features(encoded_alignment):
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
