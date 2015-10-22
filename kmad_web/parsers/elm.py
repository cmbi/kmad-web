import os
import re

from kmad_web.parsers.types import ParserError
from kmad_web.services.elm import ElmService
from kmad_web.services.geneontology import GoService
from kmad_web.parsers.geneontology import GoParser


class ElmParser(object):
    def __init__(self, elmdb_path=None):
        self._motif_instances = []
        self._motif_classes = {}
        self._elmdb_path = elmdb_path

    # Obtaining motifs for a single sequence
    def parse_instances(self, elm_txt):
        self._motif_instances = self._get_motif_instances(elm_txt)

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

    # Parse the self-made ELM DB (file created in the write_motif_classes
    # function)
    def parse_motif_classes(self):
        if not os.path.exists(self._elmdb_path):
            raise ParserError("ELM DB not found: {}".format(self._elmdb_path))
        else:
            with open(self._elmdb_path) as a:
                elm_db = a.read().splitlines()
            for line in elm_db:
                line_list = line.split()
                slim_id = line_list[0]
                self._motif_classes[slim_id] = {'probability':
                                                float(line_list[2]),
                                                'GO': line_list[3:],
                                                'regex': line_list[1],
                                                'comp_reg': re.compile(
                                                    line_list[1])
                                                }

    # Updating the ELM db
    # TODO:
    # 1. Write the file in json format? don't write it at all and stick it
    # into a database?
    # 2. Move extending the GO terms elsewhere?
    # 3. Can extending GO terms be performed by GoParser?
    def write_motif_classes(self, elm_txt, go_txt, elm_url, go_url):
        # cut out the header (6 lines)
        elm_list = elm_txt.splitlines()[6:]
        # set up the ELM and GO services
        go_service = GoService(go_url)
        go_service.get_go_terms()
        elm_service = ElmService(elm_url)
        go_parser = GoParser()
        classes_txt = []
        for line in elm_list:
            line_list = re.split('\t|"', line)
            motif_id = line_list[4]
            regex = line_list[10]
            probability = line_list[13]
            # get go terms assigned to the motif by ELM
            motif_go_terms = elm_service.get_motif_go_terms(motif_id)
            # extend the list of GO terms (based on data from the GO service)
            go_terms_extended = go_parser.extend_go_terms(go_service.go_terms,
                                                          motif_go_terms)
            go_terms_extended = ' '.join(go_terms_extended)
            classes_txt = ' '.join(motif_id, regex,
                                   probability, go_terms_extended)
        if classes_txt:
            elm_db = open(self._elmdb_path, 'w')
            elm_db.write('\n'.join(classes_txt))
            elm_db.close()
        else:
            raise ParserError("Didn't obtain any motif classes")
