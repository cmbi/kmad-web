from kmad_web.services.kmad_aligner import kmad
from kmad_web.domain.sequences.fasta import parse_fasta_alignment


def align_pairwise(sequence1, sequence2):
    fasta = ">1\n{}\n>2\n{}".format(sequence1, sequence2)

    result_fasta = kmad.align(fasta, '-12', '-1', '-1', '0', '0', '0', '',
                              gapped=True, full_ungapped=False, refine=False,
                              codon_length=1)
    sequences = parse_fasta_alignment(result_fasta)
    return sequences
