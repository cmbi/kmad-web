import logging
import tempfile


_log = logging.getLogger(__name__)


def write_fles(sequences, aligned_mode=False):
    out_text = make_fles(sequences, aligned_mode)
    tmp_file = tempfile.NamedTemporaryFile(suffix=".fasta", delete=False)
    with tmp_file as f:
        f.write(out_text)

    return tmp_file.name


def make_fles(sequences, motifs_dict, aligned_mode=False):
    out_text = ""
    sequence_key = 'encoded_seq'
    if aligned_mode:
        sequence_key = 'encoded_aligned'
    for s in sequences:
        out_text += "{}\n{}\n".format(s['header'], s[sequence_key])
    out_text += "## PROBABILITIES\n"
    for m in motifs_dict.keys():
        out_text += "{} {}\n".format(m, motifs_dict[m])
    return out_text


def parse_fles(fles_file):
    fles_lines = fles_file.splitlines()
    alignment = []
    for l in range(0, len(fles_lines), 2):
        sequence = {}
        sequence['header'] = fles_lines[l]
        sequence['encoded_seq'] = fles_lines[l + 1]
        alignment.append(sequence)
    return alignment


def get_motifs_dict(sequences):
    motifs = {}
    for s in sequences:
        for m in s['motifs']:
            if m not in motifs.keys() or \
                    s['motifs'][m]['probability'] > motifs[m]:
                motifs[m] = s['motifs'][m]['probability']
    return motifs


def fles2fasta(fles_file):
    fles_lines = fles_file.splitlines()
    fasta_lines = []
    codon_length = 7
    for line in fles_lines:
        if line.startswith('>'):
            fasta_lines.append(line)
        else:
            fasta_lines.append(line[::codon_length])
    return '\n'.join(fasta_lines)
