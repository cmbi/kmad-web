import xmltodict


class PfamParser(object):
    def __init__(self):
        self._domains = []

    @property
    def domains(self):
        return self._domains

    @domains.setter
    def domains(self, domains):
        self._domains = domains
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
        matches = pfam_dict['pfam']['results']['matches']['protein']\
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
                # information about this domain class
                domain['accession'] = m['@accession']
                domain['id'] = m['@id']
                domain['type'] = m['@type']
                domain['class'] = m['@class']
                # information about this domain location
                for k in l.keys():
                    domain[k.lstrip('@')] = l[k]
                self._domains.append(domain)

    def parse_id_result(self, pfam_result):
        pfam_dict = xmltodict.parse(pfam_result)
        if 'matches' not in pfam_dict['pfam']['entry'].keys():
            return
        matches = pfam_dict['pfam']['entry']['matches']['match']
        if not isinstance(matches, list):
            # if there are multiple domains found matches is a list, otherwise
            # it is an OrderedDict
            matches = [matches]
        for m in matches:
            # if there are multiple matches for one domain m['location']
            # is a list, otherwise it is an OrderedDict
            if 'location' in m.keys():
                if not isinstance(m['location'], list):
                    location = [m['location']]
                else:
                    location = m['location']
                for l in location:
                    domain = {}
                    # information about this domain class
                    domain['accession'] = m['@accession']
                    domain['id'] = m['@id']
                    domain['type'] = m['@type']
                    if '@class' in m.keys():
                        domain['class'] = m['@class']
                    # information about this domain location
                    for k in l.keys():
                        domain[k.lstrip('@')] = l[k]
                    self._domains.append(domain)
