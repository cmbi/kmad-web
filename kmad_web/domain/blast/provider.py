from kmad_web.services.blast import BlastService
from kmad_web.parsers.blast import BlastParser


class BlastResultProvider(object):
    """
    :param db_path: path to the BLAST database;
    """
    def __init__(self, db_path):
        self._db_path = db_path

    """
    Runs blast and returns the full result

    :param fasta_filename: path to the query fasta file
    :return: blast result
    """
    def get_result(self, fasta_filename):
        blast_service = BlastService(self._db_path)
        blast_service.run_blast(fasta_filename)
        blast_parser = BlastParser()
        blast_parser.parse(blast_service.result)
        result = blast_parser.blast_hits
        return result

    def get_exact_hit(self, blast_hits):
        print blast_hits[0]
        if (blast_hits and blast_hits[0]['slen'] == blast_hits[0]['qlen']
                and blast_hits[0]['pident'] == '100.00'):
            return blast_hits[0]['id']
