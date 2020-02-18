import logging
import re

import xml.etree.ElementTree as ET

_log = logging.getLogger(__name__)


class UniprotParser(object):
    def __init__(self):
        self.go_terms = []
        self.ptms = []
        self.structure = []

    def parse_ptms_xml(self, xml_file):
        root = ET.fromstring(xml_file)
        ns_map = {'u': 'http://uniprot.org/uniprot'}
        refs = self._get_references(root, ns_map)
        for feature_elem in root.findall('./u:entry/u:feature',
                                         namespaces=ns_map):
            type_ = feature_elem.get('type')
            if type_ == 'modified residue' or type_ == "glycosylation site":
                location_elem = feature_elem.find('u:location',
                                                  namespaces=ns_map)
                if location_elem is None:
                    continue
                position_elem = location_elem.find('u:position',
                                                   namespaces=ns_map)
                if position_elem is not None:
                    position = position_elem.get('position')
                else:
                    continue
                evidence = feature_elem.get('evidence')
                ptm = {}
                ptm['type'] = type_
                ptm['position'] = position
                ptm['info'] = feature_elem.get('description')
                if evidence:
                    ptm['eco'] = [re.sub('ECO:', '', refs[i]) for i in evidence.split()]
                else:
                    ptm['eco'] = []
                self.ptms.append(ptm)

    def _get_references(self, root, ns_map):
        references = {}
        for ref_elem in root.findall('./u:entry/u:evidence',
                                     namespaces=ns_map):
            key = ref_elem.get('key')
            type_ = ref_elem.get('type')
            references[key] = type_
        return references

    def parse_ptms(self, txt_file):
        txt_list = txt_file.splitlines()
        for i, line in enumerate(txt_list):
            if line.startswith("FT"):
                if "MOD_RES" in line or "CARBOHYD" in line:
                    feature = {
                        'type': line.split()[1],
                        'position': line.split()[2],
                        # info is on the next line
                        'info': "/".join(txt_list[i + 1].split("/")[1:]).replace("note=", "").strip('"'),
                        'pub_med': self._get_pubmed_ids(txt_list, i),
                        'eco': self._get_eco_codes(txt_list, i)
                    }
                    self.ptms.append(feature)

    def parse_structure(self, txt_file):
        strct_list = ['HELIX', 'TURN', 'STRAND', 'DISULFID', 'TRANSMEM']
        for i in txt_file.splitlines():
            if (i.startswith('FT') and len(i.split()) > 1
                    and i.split()[1] in strct_list):
                if i.split()[1] != 'DISULFID':
                    feature = {}
                    feature['name'] = i.split()[1]
                    ss_range = i.split()[-1].split(".")
                    start = ss_range[0]
                    end = ss_range[-1]
                    if start.isdigit() and end.isdigit():
                        feature['start'] = int(start)
                        feature['end'] = int(end)
                        self.structure.append(feature)
                else:
                    feature1 = {}
                    feature1['name'] = i.split()[1]
                    position = i.split()[2]
                    if position.isdigit():
                        feature1['position'] = int(position)
                        self.structure.append(feature1)
                    feature2 = {}
                    feature2['name'] = i.split()[1]
                    position = i.split()[3]
                    if position.isdigit():
                        feature2['position'] = int(position)
                        self.structure.append(feature2)

    def parse_go_terms(self, txtfile):
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
                self.go_terms.append(go_term)

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


# source: http://www.uniprot.org/help/accession_numbers
uniprot_ac_pattern = re.compile(r"^[OPQ][0-9][A-Z0-9]{3}[0-9]|[A-NR-Z][0-9]([A-Z][A-Z0-9]{2}[0-9]){1,2}$")
swissprot_id_pattern = re.compile(r"^[A-Z][A-Z0-9]+_[A-Z]+$")

def valid_uniprot_id(uniprot_id):
    return uniprot_ac_pattern.match(uniprot_id) or \
           swissprot_id_pattern.match(uniprot_id)
