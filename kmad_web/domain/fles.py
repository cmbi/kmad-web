import os
import tempfile


def write_fles(sequences):
    out_text = ""
    for s in sequences:
        out_text += "{}\n{}\n".format(s['header'], s['encoded_seq'])

    tmp_file = tempfile.NamedTemporaryFile(suffix=".fasta", delete=False)
    with tmp_file as f:
        f.write(out_text)

    return tmp_file.name


def parse_fles(fles_path):
    if not os.path.exists(fles_path):
        raise RuntimeError("Alignment file not found")
    else:
        with open(fles_path) as a:
            fles = a.read().splitlines()
        alignment = []
        for l in range(0, len(fles), 2):
            sequence = {}
            sequence['header'] = fles[l]
            sequence['encoded_seq'] = fles[l + 1]
            alignment.append(sequence)
        return alignment
