import logging
import re

from kmad_web.helpers.txtproc import unwrap


logging.basicConfig()
_log = logging.getLogger(__name__)


class UniprotParser(object):
    def __init__(self):
        self._go_terms = []
        self._features = []

    def parse_txt(self, txt_file):
        self._go_terms = self._get_go_terms(txt_file)
        self._features = self._get_features(txt_file)

    def parse_fasta(self, fastafile):
        fasta_seq = unwrap(fastafile)
        return fasta_seq

    def _get_features(self, txt_file):
        txt_list = txt_file.splitlines()
        features = []
        for i, line in enumerate(txt_list):
            if line.startswith("FT"):
                if "MOD_RES" in line or "CARBOHYD" in line:
                    feature = {}
                    feature['type'] = line.split()[1]
                    feature['position'] = line.split()[2]
                    feature['info'] = ' '.join(line.split()[4:])
                    feature['pub_med'] = self._get_pubmed_ids(txt_list, i)
                    feature['eco'] = self._get_eco_codes(txt_list, i)
                    features.append(feature)
        return features

    def _get_go_terms(self, txtfile):
        go_terms = []
        for line in txtfile.splitlines():
            if line.startswith("DR   GO;"):
                go_term = {}
                reg = re.compile("GO:(?P<code>[0-9]{7}); (?P<type>F|P|C):"
                                 "(?P<desc>[^;]+); (?P<src>[^.]+)")
                match_dict = reg.search(line).groupdict()
                go_term['code'] = match_dict['code']
                go_term['type'] = match_dict['type']
                go_term['description'] = match_dict['desc']
                go_term['source'] = match_dict['src']
                go_terms.append(go_term)
        return go_terms

    def _get_pubmed_ids(self, txt_list, index):
        pubmed_ids = set()
        reg = re.compile("PubMed:(?P<id>[0-9]+)")
        in_feature_section = True
        i = index
        while in_feature_section and i < len(txt_list):
            line = txt_list[i]
            if i > index and not line.startswith("FT          "):
                in_feature_section = False
            else:
                for match in reg.finditer(line):
                    pubmed_id = match.groupdict()['id']
                    pubmed_ids.add(pubmed_id)
                i += 1
        return pubmed_ids

    def _get_eco_codes(self, txt_list, index):
        eco_codes = []
        reg = re.compile("ECO:(?P<code>[0-9]{7})")
        in_feature_section = True
        i = index
        while in_feature_section and i < len(txt_list):
            line = txt_list[i]
            if i > index and not line.startswith("FT          "):
                in_feature_section = False
            else:
                for match in reg.finditer(line):
                    eco = match.groupdict()['code']
                    if eco not in eco_codes:
                        eco_codes.append(eco)
                i += 1
        return eco_codes
