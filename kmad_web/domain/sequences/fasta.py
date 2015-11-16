import logging
import re

_log = logging.getLogger(__name__)


def unwrap(fasta):
    new = []
    for i in fasta:
        if i.startswith('>'):
            new.append(i)
            new.append("")
        else:
            new[-1] += i
    return new


def parse_fasta(fastafile):
    fasta_data = unwrap(fastafile.splitlines())
    sequences = []
    for i in range(0, len(fasta_data), 2):
        sequence = {
            'header': fasta_data[i],
            'seq': fasta_data[i + 1]
        }
        sequences.append(sequence)
    return sequences


def parse_fasta_alignment(fastafile):
    fasta_data = unwrap(fastafile.splitlines())
    sequences = []
    for i in range(0, len(fasta_data), 2):
        sequence = {
            'header': fasta_data[i],
            'aligned': fasta_data[i + 1],
            'seq': re.sub('-', '', fasta_data[i + 1])
        }
        sequences.append(sequence)
    return sequences


def make_fasta(sequence_data):
    if check_fasta(sequence_data):
        return sequence_data
    else:
        if not ''.join(sequence_data.split()).isalpha():
            raise RuntimeError("Sequence has to consist of only alphabetic "
                               "characters: {}".format(sequence_data))
        return ">sequence\n{}\n".format(sequence_data)


def sequences2fasta(sequences):
    fasta = ""
    for s in sequences:
        fasta += "{}\n{}\n".format(s['header'], s['seq'])
    return fasta


def alpha_or_dash(sequence):
    check1 = len(''.join(sequence.split())) > 0
    check2 = all([i.isalpha() or i == '-' for i in sequence])
    return check1 and check2


def check_fasta(sequence_data):
    data_lines = sequence_data.splitlines()
    fasta_header_count = ''.join(data_lines).count('>')
    alright = True
    if fasta_header_count > 0:
        # check if first is a header, and last is not a header,
        # and last is alphabetic
        alright = (data_lines[0].startswith('>')
                   and not data_lines[-1].startswith('>')
                   and alpha_or_dash(data_lines[-1]))
        if alright:
            for i, lineI in enumerate(data_lines[:-1]):
                fasta_header = lineI.startswith('>')
                if fasta_header and not alpha_or_dash(data_lines[i + 1]):
                    raise RuntimeError("This line is a header "
                                       "but next is not a sequence:\n{}".format(
                                           data_lines[i + 1]
                                       ))
                elif not fasta_header and not alpha_or_dash(lineI):
                    raise RuntimeError("Line that is not a header"
                                       " and is not a sequence:\n{}".format(
                                           data_lines[i + 1]
                                       ))
    else:
        alright = False
    return alright


def get_first_seq(fasta_sequences):
    first_seq = '\n'.join(unwrap(fasta_sequences.splitlines())[:2])
    return first_seq
