
class BlastParser(object):
    """
    :param db: 'swiss' or nothing
    """
    def __init__(self, db='swiss'):
        self.blast_hits = []
        self._swiss_db = True if db == 'swiss' else False

    def parse(self, blast_result):
        for l in blast_result.splitlines():
            blast_hit = {}
            line_list = l.split(',')
            blast_hit['header'] = line_list[1]
            if self._swiss_db:
                blast_hit['entry_name'] = line_list[1].split('|')[2]
                blast_hit['id'] = line_list[1].split('|')[1]
            blast_hit['pident'] = line_list[2]
            blast_hit['mismatch'] = line_list[3]
            blast_hit['evalue'] = line_list[4]
            blast_hit['bitscore'] = line_list[5]
            blast_hit['slen'] = line_list[6]
            blast_hit['qlen'] = line_list[6]
            self.blast_hits.append(blast_hit)
