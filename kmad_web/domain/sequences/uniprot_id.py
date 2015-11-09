import os
import tempfile

from kmad_web.default_settings import BLAST_DB
from kmad_web.domain.blast.provider import BlastResultProvider


def get_uniprot_id(sequence):
    fasta_sequence = ">sequence\n{}\n".format(sequence)
    tmp_file = tempfile.NamedTemporaryFile(suffix=".fasta", delete=False)
    with tmp_file as f:
        f.write(fasta_sequence)
    blast = BlastResultProvider(BLAST_DB)
    blast_result = blast.get_result(tmp_file.name)
    seq_id = blast.get_exact_hit(blast_result)
    os.remove(tmp_file.name)
    return seq_id
