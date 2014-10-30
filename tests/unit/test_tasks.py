from mock import mock_open, patch
from nose.tools import eq_, raises

from testdata import test_variables as test
from kman_web.factory import create_app, create_celery_app


class TestTasks(object):

    @classmethod
    def setup_class(cls):
        flask_app = create_app({'TESTING': True,
                                'CELERY_ALWAYS_EAGER': True
                                })
        cls.celery = create_celery_app(flask_app)

    def test_get_seq(self):
        output = test.seq

        from kman_web.tasks import get_seq

        result = get_seq.delay('d2p2', '>test\nSEQ\n')
        eq_(result.get(), output)

    @patch('kman_web.tasks.convert_to_7chars')
    @patch('kman_web.tasks.get_fasta_from_blast')
    @patch('subprocess.call')
    @patch('kman_web.tasks.open',
           mock_open(read_data=test.alignment_7c),
           create=True)
    def test_align(self, mock_subprocess, mock_call1, mock_call2):
        filename = 'testdata/test.fasta'
        mock_call1.return_value = 'testdata/test.blastp'
        mock_call2.return_value = 'testdata/test.7c'
        expected = [test.alignment_1c, test.alignment_1c_list]

        from kman_web.tasks import align

        result = align.delay('d2p2', filename)
        eq_(result.get(), expected)

    def test_postprocess(self):
        filename = 'testdata/test.fasta'

        from kman_web.tasks import postprocess

        # check d2p2 result and output type 'predict'
        func_input = [test.seq, test.d2p2_result]
        expected = func_input[:]

        result = postprocess.delay(func_input, filename, 'predict')
        eq_(result.get(), expected)

        # check predictors' result and output type 'predict'
        func_input = [test.seq] + test.pred_result
        expected = [test.seq] + test.processed_pred_result

        result = postprocess.delay(func_input, filename, 'predict')
        eq_(result.get(), expected)

        # check d2p2 results and output type 'predict_and_align'
        func_input = [test.seq] \
            + [test.d2p2_result] \
            + [[test.alignment_1c, test.alignment_1c_list]]
        expected = func_input[:]

        result = postprocess.delay(func_input, filename, 'predict_and_align')
        eq_(result.get(), expected)

        # check predictors' results and output type 'predict_and_align'
        func_input = [test.seq] \
            + test.pred_result \
            + [[test.alignment_1c, test.alignment_1c_list]]
        expected = [test.seq] \
            + test.processed_pred_result \
            + [[test.alignment_1c, test.alignment_1c_list]]

        result = postprocess.delay(func_input, filename, 'predict_and_align')
        eq_(result.get(), expected)

    def test_get_task(self):
        output_type = 'predict'

        from kman_web.tasks import get_task, postprocess

        expected = postprocess
        result = get_task(output_type)
        eq_(result, expected)

    @raises(ValueError)
    def test_get_value_error(self):
        output_type = 'incorrect_value'

        from kman_web.tasks import get_task

        get_task(output_type)

    @patch('kman_web.tasks.find_seqid_blast')
    @patch('subprocess.call')
    def test_query_d2p2(self, mock_subprocess, mock_call):
        filename = 'testdata/test.fasta'
        mock_subprocess.return_value = 'testdata/test.blastp'

        from kman_web.tasks import query_d2p2

        # check: sequence not found in swissprot
        mock_call.return_value = [False, '']
        expected = [False, []]

        result = query_d2p2.delay(filename)
        eq_(result.get(), expected)

        # check: sequence found in swissprot, but not found in d2p2
        mock_call.return_value = [True, 'P01542']
        expected = [False, []]

        result = query_d2p2.delay(filename)
        eq_(result.get(), expected)

        # check: sequence found in d2p2
        mock_call.return_value = [True, 'P10636']

        result = query_d2p2.delay(filename).get()
        eq_(result[0], True)

    @patch('kman_web.tasks.preprocess')
    @patch('subprocess.call')
    @patch('kman_web.tasks.open',
           mock_open(read_data='prediction_out'),
           create=True)
    def test_run_single_predictor(self, mock_subprocess, mock_call):
        filename = 'testdata/test.fasta'
        methods = ['psipred', 'predisorder', 'disopred', 'spine']
        pred = [0, 0, 0]

        from kman_web.tasks import run_single_predictor

        # check when there is no result from d2p2
        d2p2_result = [False, []]
        for pred_name in methods:
            expected = [pred_name, pred]
            mock_call.return_value = expected[:]

            result = run_single_predictor.delay(d2p2_result,
                                                filename,
                                                pred_name)
            eq_(result.get(), expected)

        # check when there is result from d2p2
        d2p2_result = [True, ['D2P2', [0, 0, 0]]]
        expected = d2p2_result[1]

        result = run_single_predictor.delay(d2p2_result, filename, pred_name)
        eq_(result.get(),  expected)
