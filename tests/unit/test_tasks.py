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
                                    process_kmad_alignment, analyze_mutation)

        output_type = 'predict'
        expected = process_prediction_results
        result = get_task(output_type)
        eq_(result, expected)

        output_type = 'align'
        expected = process_kmad_alignment
        result = get_task(output_type)
        eq_(result, expected)

        output_type = 'ptms'
        expected = analyze_mutation
        result = get_task(output_type)
        eq_(result, expected)

        output_type = 'motifs'
        expected = analyze_mutation
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
        methods = ['psipred', 'predisorder', 'disopred', 'spine', 'globplot']

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
