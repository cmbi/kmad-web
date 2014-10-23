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
        

    @patch('subprocess.call')
    @patch('kman_web.tasks.open', mock_open(read_data=alignment_7c), create=True)
    @patch('kman_web.tasks.get_fasta_from_blast')
    @patch('kman_web.tasks.convert_to_7chars')
    def test_align(self, mock_subprocess, mock_call1, mock_call2):
        filename = 'testdata/test.fasta'
        mock_call1.return_value = 'testdata/test.blastp'
        mock_call2.return_value = 'testdata/test.7c'
        expected = [alignment_1c, alignment_1c_list]

        from kman_web.tasks import align

        result = align.delay('d2p2', filename)
        eq_(result.get(), expected)


    def test_postprocess(self):
        filename = 'testdata/test.fasta'
    
        from kman_web.tasks import postprocess
        
        ## check d2p2 result and output type 'predict'
        func_input = [seq, d2p2_result]
        expected = func_input

        result = postprocess.delay(func_input, filename, 'predict')
        eq_(result.get(), expected)

        ## check predictors result and output type 'predict'
        func_input = [seq] + pred_result + [[alignment_1c, alignment_1c_list]]
        expected = func_input
        print func_input

        result = postprocess.delay(func_input, filename, 'predict')
        eq_(result.get(), expected)
        





        
               



 
