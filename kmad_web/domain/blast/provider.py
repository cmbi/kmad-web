from kmad_web.services.blast import BlastService
from kmad_web.parsers.blast import BlastParser
from kmad_web.default_settings import BLAST_DB


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
    def get_result(self, fasta_sequence, seq_limit):
        blast_service = BlastService(self._db_path)
        blast_result = blast_service.run_blast(fasta_sequence, seq_limit)
        blast_parser = BlastParser()
        blast_parser.parse(blast_result)
        filtered = self._filter_out_duplicates(blast_parser.blast_hits)
        return filtered

    def get_exact_hit(self, blast_hits):
        if (blast_hits and blast_hits[0]['slen'] == blast_hits[0]['qlen']
                and blast_hits[0]['pident'] == '100.00'):
            return blast_hits[0]['id']
        else:
            return ''

    def find_closest_hit(self, fasta_sequence, seq_limit=1):
        blast_hits = self.get_result(fasta_sequence, seq_limit)
        if float(blast_hits[0]['pident']) >= 80:
            return blast_hits[0]
        else:
            return ''

    def _filter_out_duplicates(self, blast_hits):
        filtered_hits = []
        ids_set = set()
        for h in blast_hits:
            if h['id'] not in ids_set:
                filtered_hits.append(h)
                ids_set.add(h['id'])
        return filtered_hits


blast = BlastResultProvider(BLAST_DB)
