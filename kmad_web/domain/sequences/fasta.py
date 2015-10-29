

def unwrap(fasta):
    new = []
    for i in fasta:
        if i.startswith('>'):
            new.append(i)
            new.append("")
        else:
            new[-1] += i
    return new


def parse_fasta(self, fastafile):
    fasta_sequence = unwrap(fastafile)
    return fasta_sequence
