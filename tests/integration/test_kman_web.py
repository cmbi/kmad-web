import logging
_log = logging.getLogger(__name__)

sh = logging.StreamHandler()
formatter = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s')
sh.setFormatter(formatter)
_log.addHandler(sh)
_log.setLevel(logging.DEBUG)

import json
import os
import random
import time

import requests
from nose.tools import eq_

from kman_web import paths


KMAN_URL = 'http://127.0.0.1:5000/api/'
FMT_CREATE = '{}create/{}/'
FMT_STATUS = '{}status/{}/{}/'


class TestApi(object):

    def setup(self):
        self.all_uniprot_ids = self._get_uniprot_ids()

    def _get_uniprot_ids(self):
        uni_ids = [i for i in os.listdir(paths.UNIPROT_FASTA_DIR)]
        return uni_ids

    def _get_random_sequences(self, n):
        random_ids = [random.choice(self.all_uniprot_ids) for i in range(0, n)]
        random_sequences = []
        for i in random_ids:
            with open('{}/{}'.format(paths.UNIPROT_FASTA_DIR, i)) as a:
                random_sequences += [a.read()]
        random_ids = [i.split('.')[0] for i in random_ids]
        return random_sequences, random_ids

    def _test_sequences(self, output_types, test_sequences, test_ids):
        for i in range(len(test_sequences)):
            sequence = test_sequences[i]
            seq_id = test_ids[i]
            _log.info('Testing {}...'.format(seq_id))
            for output_type in output_types:
                _log.info('Getting {} for {}...'.format(output_type,
                                                        seq_id))
                url_create = FMT_CREATE.format(KMAN_URL,
                                               output_type)

                r = requests.post(url_create, data={'data': sequence})
                r.raise_for_status()
                job_id = json.loads(r.text)['id']

                while True:
                    url_status = FMT_STATUS.format(KMAN_URL,
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
                        _log.debug('Waiting 10 more seconds...')
                        time.sleep(10)
                _log.info('Done!')

    def test_sequence_predict(self):
        """Tests that disorder can be predicted for random sequences.

        The test tries to get 5 randomly chosen sequences from Uniprot
        and perform disorder prediction and alignment (or prediction only)
        using the KMAN API
        """
        n = 1
        test_sequences, test_ids = self._get_random_sequences(n)
        _log.info("Testing {} a random sequence: {}".format(n, test_ids))
        self._test_sequences(['predict', 'predict_and_align', 'align'],
                             test_sequences,
                             test_ids)
