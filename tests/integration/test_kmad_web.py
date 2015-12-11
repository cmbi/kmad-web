import logging
_log = logging.getLogger(__name__)

sh = logging.StreamHandler()
formatter = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s')
sh.setFormatter(formatter)
_log.addHandler(sh)
_log.setLevel(logging.DEBUG)

import json
import random
import requests
import time

from nose.tools import eq_


KMAD_URL = 'http://127.0.0.1:5000/api/'
FMT_CREATE = '{}create/{}/'
FMT_STATUS = '{}status/{}/{}/'


class TestApi(object):

    def _test_sequences(self, test_sequences):
        for i in range(len(test_sequences)):
            for sequence in test_sequences:
                _log.info("testing sequence: {}".format(
                    sequence.splitlines()[0].split()[0]
                ))
                output_types = ['predict', 'ptms', 'motifs', 'refine', 'align']
                for output_type in output_types:
                    _log.info("Testing output_type: {}".format(output_type))
                    url_create = FMT_CREATE.format(KMAD_URL, output_type)
                    data = self._get_data(output_type, sequence)
                    _log.debug("Posting data: {}".format(data))
                    r = requests.post(url_create, data=data)
                    r.raise_for_status()
                    job_id = json.loads(r.text)['id']

                    while True:
                        url_status = FMT_STATUS.format(KMAD_URL,
                                                       output_type,
                                                       job_id)
                        r = requests.get(url_status)
                        r.raise_for_status()

                        status = json.loads(r.text)['status']
                        msg = None
                        try:
                            msg = json.loads(r.text)['message']
                        except KeyError:
                            pass

                        if status in ['SUCCESS', 'FAILURE', 'REVOKED']:
                            eq_(status,
                                'SUCCESS', "{} - {} failed: '{}'".format(
                                    output_type, sequence, msg))
                            break
                        else:
                            time.sleep(10)
                    _log.info('Done!')

    def test_sequence(self):
        """Tests that disorder can be predicted for random sequences.

        The test tries to get 5 randomly chosen sequences from Uniprot
        and perform all actions
        using the KMAD API
        """
        test_sequences = [self._get_random_sequence() for i in range(1)]
        self._test_sequences(test_sequences)

    def _get_data(self, output_type, fasta_content):
        if output_type == 'align':
            data = {'seq_data': fasta_content,
                    'gop': -12, 'gep': -1.2,
                    'egp': -1.2, 'ptm_score': 3,
                    'domain_score': 10, 'motif_score': 3,
                    'usr_features': [],
                    'output_type': output_type,
                    'gapped': False, 'seq_limit': 35}
        elif output_type == 'predict':
            prediction_methods = 'globplot'
            data = {'seq_data': fasta_content,
                    'prediction_methods': prediction_methods}
        elif output_type == 'refine':
            data = {'seq_data': fasta_content,
                    'gop': -12, 'gep': -1.2,
                    'egp': -1.2, 'ptm_score': 3,
                    'domain_score': 10, 'motif_score': 3,
                    'usr_features': [],
                    'output_type': output_type,
                    'gapped': False, 'alignment_method': 'clustalo',
                    'seq_limit': 35}
        elif output_type == 'ptms':
            position = self._get_random_position(fasta_content)
            mutant_aa = self._get_random_mutant_aa(position, fasta_content)
            data = {'seq_data': fasta_content,
                    'position': position,
                    'mutant_aa': mutant_aa
                    }
        elif output_type == 'motifs':
            position = self._get_random_position(fasta_content)
            mutant_aa = self._get_random_mutant_aa(position, fasta_content)
            data = {'seq_data': fasta_content,
                    'position': position,
                    'mutant_aa': mutant_aa
                    }

        return data

    def _get_random_position(self, fasta_content):
        seq_length = len(''.join(fasta_content.splitlines()[1:]))
        return random.randrange(0, seq_length)

    def _get_random_mutant_aa(self, position, fasta_content):
        aas = ['A', 'R', 'N', 'D', 'C', 'M', 'P', 'T', 'Y', 'W',
               'E', 'Q', 'L', 'I', 'V', 'F', 'K', 'G', 'H', 'S']
        wild_aa = ''.join(fasta_content.splitlines()[1:])[position]
        aas.remove(wild_aa)
        rand_int = random.randrange(0, 19)
        return aas[rand_int]

    def _get_random_sequence(self):
        response = requests.get(
            'http://uniprot.org/uniprot/?query=protein&random=yes&format=fasta&fil=reviewed:yes')
        fasta = response.text
        random_cut = random.choice([True, False])
        if random_cut:
            left_cut = random.choice([True, False])
            if left_cut:
                fasta = fasta.splitlines()[0] + '\n' + ''.join(fasta.splitlines()[1:])[1:]
                _log.info("N-terminal cut")
            else:
                fasta = fasta[:-1]
                _log.info("C-terminal cut")
        else:
            _log.info("Full sequence")
        return fasta
