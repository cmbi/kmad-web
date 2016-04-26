import logging
import os
import re


_log = logging.getLogger(__name__)


class PhosphositeParser(object):
    def __init__(self, path=None):
        self._path = path

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, path):
        self._path = path

    def get_ptm_sites(self, uniprot_id, ptm_type):
        filename = {
            'phosph': 'Phosphorylation_site_dataset',
            'acet': 'Acetylation_site_dataset',
            'meth': 'Methylation_site_dataset'
        }
        ptm_sites = []
        full_path = os.path.join(self._path, filename[ptm_type])
        if os.path.exists(full_path):
            with open(full_path) as a:
                psite_db = a.read()
            ptm_sites = self.parse_db(psite_db, uniprot_id)
        else:
            _log.warning("Database not found: {}".format(full_path))
        return ptm_sites

    def parse_db(self, psite_db, uniprot_id):
        psite_db = psite_db.splitlines()
        positions = []
        in_sequence_section = False
        for lineI in psite_db:
            if not in_sequence_section and uniprot_id in lineI:
                # start looking for ptms
                in_sequence_section = True
            if in_sequence_section and uniprot_id in lineI:
                # take ptm and add it to dict
                reg = re.compile("[A-Z](?P<pos>[0-9]{1,5})[-][a-z]")
                matches = list(reg.finditer(lineI))
                if len(matches) == 1:
                    position = matches[0].groupdict()['pos']
                    if position.isdigit():
                        positions.append(position)
                    else:
                        _log.info("Couldn't get position from line:\n{}".format(
                            lineI))
            elif in_sequence_section:
                # means it has already read all the entries for this sequence
                break
        return positions
