import subprocess

from mock import ANY, call, mock_open, patch
from nose.tools import eq_, raises

from testdata.test_variables import *
from kman_web.factory import create_app, create_celery_app


class TestTasks(object):

    @classmethod
    def setup_class(cls):
        flask_app = create_app({'TESTING': True,
                                'CELERY_ALWAYS_EAGER': True
                                })
        cls.celery = create_celery_app(flask_app)

    def test_get_seq(self):
        output = seq
    
        from kman_web.tasks import get_seq
    
        result = get_seq.delay('d2p2','>test\nSEQ\n')
        eq_(result.get(), output)
        

    @patch('kman_web.tasks.convert_to_7chars')
    @patch('kman_web.tasks.get_fasta_from_blast')
    @patch('subprocess.call')
    @patch('kman_web.tasks.open', mock_open(read_data=alignment_7c), create=True)
    def test_align(self, mock_subprocess, mock_call1, mock_call2):
        filename = 'testdata/test.fasta'
        mock_call1.return_value = 'testdata/test.blastp'
        mock_call2.return_value = 'testdata/test.7c'
        expected = [alignment_1c, alignment_1c_list]

        from kman_web.tasks import align

        result = align.delay('d2p2', filename)
        eq_(result.get(), expected)


    @patch('kman_web.tasks.convert_to_7chars')
    @patch('kman_web.tasks.get_fasta_from_blast')
    @patch('subprocess.call')
    @patch('kman_web.tasks.open', mock_open(read_data=alignment_7c), create=True)
    @raises(RuntimeError)
    def test_align_subprc_error(self, mock_subprocess, mock_call1, mock_call2):
        mock_call1.return_value = 'testdata/test.blastp'
        mock_call2.return_value = 'testdata/test.7c'
        filename = 'testdata/test.fasta'
        mock_subprocess.side_effect = subprocess.CalledProcessError(
            "returncode", "cmd", "output")
        from kman_web.tasks import align
        result = align.delay('d2p2', filename)
        result.get()


    def test_postprocess(self):
        filename = 'testdata/test.fasta'
    
        from kman_web.tasks import postprocess
        
        ## check d2p2 result and output type 'predict'
        func_input = [seq, d2p2_result]
        expected = func_input[:]

        result = postprocess.delay(func_input, filename, 'predict')
        eq_(result.get(), expected)

        ## check predictors' result and output type 'predict'
        func_input = [seq] + pred_result 
        expected = [seq] + processed_pred_result

        result = postprocess.delay(func_input, filename, 'predict')
        a = result.get()
        eq_(result.get(), expected)
        
        # check d2p2 results and output type 'predict_and_align'
        func_input = [seq] + [d2p2_result] + [[alignment_1c, alignment_1c_list]]
        expected = func_input[:]

        result = postprocess.delay(func_input, filename, 'predict_and_align')
        eq_(result.get(), expected)

        # check predictors' results and output type 'predict_and_align'
        func_input = [seq] + pred_result + [[alignment_1c, alignment_1c_list]]
        expected = [seq] + processed_pred_result + [[alignment_1c, alignment_1c_list]]
        
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
        mock_call.return_value = [False, '']

        from kman_web.tasks import query_d2p2

        ## check: sequence not found in swissprot
        expected = [False, []]

        result = query_d2p2.delay(filename)
        eq_(result.get(), expected)



    @patch('subprocess.call')
    @raises(RuntimeError)
    def test_query_d2p2_subprc_error(self, mock_subprocess):
        filename = 'testdata/test.fasta'
        mock_subprocess.side_effect = subprocess.CalledProcessError(
            "returncode", "cmd", "output")
        
        from kman_web.tasks import query_d2p2

        result = query_d2p2.delay(filename)
        result.get()
        
        
        
        

    def test_run_single_predictor(self):
        pass
        
    
  
    

    
           



 
