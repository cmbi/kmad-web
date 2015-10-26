import xmltodict
class PfamParser(object):
    def __init__(self):
        self._domains = []

    """
    output = [
              {
                'acc': domain_accession
                'start': start_index
                'end': end_index
              }
             ]
    """
    def parse(self, pfam_result):
        pfam_dict = xmltodict.parse(pfam_result)
        matches = pfam_dict['pfam']['results']['matches']['protein'] \
                           ['database']['match']
        if not isinstance(matches, list):
            # if there are multiple domains found matches is a list, otherwise
            # it is an OrderedDict
            matches = [matches]
        for m in matches:
            # if there are multiple matches for one domain m['location']
            # is a list, otherwise it is an OrderedDict
            if not isinstance(m['location'], list):
                location = [m['location']]
            else:
                location = m['location']
            for l in location:
                domain = {}
                domain['acc'] = m['@accession']
                domain['start'] = l['@start']
                domain['end'] = l['@end']
                self._domains.append(domain)
