import json
import os
import re

from kmad_web.parsers.types import ParserError


class ElmParser(object):
    def __init__(self, elmdb_path=None):
        self.motif_instances = []
        self.motif_classes = {}
        self.full_motif_classes = {}
        self._elmdb_path = elmdb_path

    # Obtaining motifs for a single sequence
    def parse_instances(self, elm_txt):
        self.motif_instances = self._get_motif_instances(elm_txt)

    def _get_motif_instances(self, elm_txt):
        motifs = []
        elm_list = elm_txt.splitlines()
        for line in elm_list:
            if "sequence_feature" in line:
                motif = {}
                motif['id'] = line.split()[8].split('=')[1]
                motif['start'] = int(line.split()[3])
                motif['end'] = int(line.split()[4])
                motifs.append(motif)
        return motifs

    # Parse the self-made ELM DB (json file created in the write_motif_classes
    # function)
    # TODO: cache
    def parse_full_motif_classes(self):
        if not os.path.exists(self._elmdb_path):
            raise ParserError("ELM DB not found: {}".format(self._elmdb_path))
        else:
            with open(self._elmdb_path) as a:
                elm_db = a.read()
            self.full_motif_classes = json.loads(elm_db)

    # parse motif classes obtained from ELM (elm_classes.tsv)
    def parse_motif_classes(self, elm_data):
        elm_list = elm_data.splitlines()
        header_len = 6
        for line in elm_list[header_len:]:
            line_list = [i.rstrip('"').lstrip('"')
                         for i in re.split(r'\t+', line)]
            elm_id = line_list[1]
            self.motif_classes[elm_id] = {}
            self.motif_classes[elm_id]['class'] = line_list[2].rstrip('.')
            self.motif_classes[elm_id]['pattern'] = line_list[3]
            self.motif_classes[elm_id]['probability'] = line_list[4]
