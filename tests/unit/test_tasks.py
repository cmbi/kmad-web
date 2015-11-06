from mock import mock_open, patch
from nose.tools import eq_, ok_, raises

from kmad_web.factory import create_app, create_celery_app


class TestTasks(object):

    @classmethod
    def setup_class(cls):
        flask_app = create_app({'TESTING': True,
                                'CELERY_ALWAYS_EAGER': True
                                })
        cls.celery = create_celery_app(flask_app)

    def test_get_task(self):

        from kmad_web.tasks import (get_task, process_prediction_results,
                                    process_kmad_alignment, analyze_ptms,
                                    analyze_motifs)

        output_type = 'predict'
        expected = process_prediction_results
        result = get_task(output_type)
        eq_(result, expected)

        output_type = 'align'
        expected = process_kmad_alignment
        result = get_task(output_type)
        eq_(result, expected)

        output_type = 'ptms'
        expected = analyze_ptms
        result = get_task(output_type)
        eq_(result, expected)

        output_type = 'motifs'
        expected = analyze_motifs
        result = get_task(output_type)
        eq_(result, expected)

    @raises(ValueError)
    def test_get_value_error(self):
        output_type = 'incorrect_value'

        from kmad_web.tasks import get_task

        get_task(output_type)

    def test_query_d2p2(self):
        from kmad_web.tasks import query_d2p2

        # check: sequence not found in swissprot
        blast_result = {
            'exact_hit': {'found': False}
        }
        expected = None

        result = query_d2p2(blast_result)
        eq_(result, expected)

        # check: sequence found in d2p2
        blast_result = {
            'exact_hit': {'found': True, 'seq_id': 'P10636'}
        }
        result = query_d2p2(blast_result)
        ok_(result)

    @patch('kmad_web.tasks.os.path.exists')
    @patch('kmad_web.tasks.PredictionProcessor.process_prediction')
    @patch('subprocess.call')
    @patch('subprocess.check_output')
    @patch('kmad_web.tasks.open',
           mock_open(read_data='prediction_out'),
           create=True)
    def test_run_single_predictor(self, mock_subprocess, mock_call,
                                  mock_check_output, mock_os):
        filename = 'testdata/test.fasta'
        methods = ['psipred', 'predisorder', 'disopred', 'spine', 'globplot',
                   'iupred']

        pred = [1, 1, 2]
        mock_os.return_value = True

        from kmad_web.tasks import run_single_predictor

        for pred_name in methods:
            expected = {pred_name: pred}
            mock_call.return_value = pred
            mock_check_output.return_value = pred

            result = run_single_predictor(filename, pred_name)
            eq_(result, expected)

        result = run_single_predictor(filename, pred_name)
        eq_(result,  expected)

    def test_process_prediction_results(self):
        fasta_seq = '>1\nSEQSEQ\n'
        predictions_in = [
            {'disopred': [0, 0, 0, 0, 2, 2]},
            {'predisorder': [2, 2, 0, 0, 2, 2]}
        ]

        from kmad_web.tasks import process_prediction_results

        result = process_prediction_results(predictions_in, fasta_seq)
        expected = {
            'prediction': {
                'disopred': [0, 0, 0, 0, 2, 2],
                'predisorder': [2, 2, 0, 0, 2, 2],
                'consensus': [1, 1, 0, 0, 2, 2],
                'filtered': [1, 1, 0, 0, 2, 2]
            },
            'sequence': 'SEQSEQ'
        }
        eq_(expected, result)

    @patch('kmad_web.tasks.tempfile')
    @patch('kmad_web.tasks.TcoffeeService')
    @patch('kmad_web.tasks.MuscleService')
    @patch('kmad_web.tasks.MafftService')
    @patch('kmad_web.tasks.ClustalwService')
    @patch('kmad_web.tasks.ClustaloService')
    @patch('kmad_web.tasks.open', mock_open(read_data='>1\nSEQSEQ\n'),
           create=True)
    def test_prealign(self, mock_clustalo, mock_clustalw, mock_mafft,
                      mock_muscle, mock_tcoffee, mock_temp):

        from kmad_web.tasks import prealign

        methods = ['clustalo', 'clustalw', 'mafft', 'muscle', 't_coffee']
        fasta_seq = '>1\nSEQSEQ\n'
        expected = [{'seq': 'SEQSEQ', 'header': '>1'}]
        for m in methods:
            result = prealign(fasta_seq, m)
            eq_(expected, result)

    @patch('kmad_web.tasks.tempfile')
    @patch('kmad_web.tasks.BlastResultProvider.get_result')
    @patch('kmad_web.tasks.BlastResultProvider.get_exact_hit')
    def test_run_blast(self, mock_hit, mock_res, mock_tmp):

        from kmad_web.tasks import run_blast

        fasta_seq = '>1\nSEQSEQ\n'

        mock_res.return_value = 'blast_result'
        mock_hit.return_value = 'exact_hit'
        expected = {
            'blast_result': 'blast_result',
            'exact_hit': {
                'seq_id': 'exact_hit',
                'found': True
            }
        }
        eq_(expected, run_blast(fasta_seq))

        mock_hit.return_value = 'exact_hit'
        expected = {
            'blast_result': 'blast_result',
            'exact_hit': {
                'seq_id': 'exact_hit',
                'found': True
            }
        }
        eq_(expected, run_blast(fasta_seq))
