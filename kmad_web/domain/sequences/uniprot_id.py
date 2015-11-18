from kmad_web.default_settings import BLAST_DB
from kmad_web.domain.blast.provider import BlastResultProvider


def get_uniprot_id(sequence):
    fasta_sequence = ">sequence\n{}\n".format(sequence)
    blast = BlastResultProvider(BLAST_DB)
    blast_result = blast.get_result(fasta_sequence)
    seq_id = blast.get_exact_hit(blast_result)
    return seq_id
