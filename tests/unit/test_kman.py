from mock import patch
from nose.tools import eq_, ok_, raises

from testdata.test_variables import *
from kman_web.factory import create_app, create_celery_app

class TestKman(object):

    @classmethod
    def setup_class(cls):
        flask_app = create_app({'TESTING': True,
                                'CELERY_ALWAYS_EAGER': True
                                })
        cls.celery = create_celery_app(flask_app)

    def test_kman_strategy_factory(self):
        from kman_web.services.kman import (KmanStrategyFactory, PredictStrategy, 
                                            PredictAndAlignStrategy)
        strategy = KmanStrategyFactory.create('predict')
        ok_(isinstance(strategy, PredictStrategy))
        strategy = KmanStrategyFactory.create('predict_and_align')
        ok_(isinstance(strategy, PredictAndAlignStrategy))
    
    
    @raises(ValueError)
    def test_kman_strategy_factory_unexpected_output_type(self):
        from kman_web.services.kman import KmanStrategyFactory

        KmanStrategyFactory.create('unexpected')
    
    
    ## TODO finish test_predict_strategy, and add test_predict_and_align_strategy  
    @patch('celery.chain')
    #@patch('kman_web.services.kman.PredictStrategy.__call__.chain')
    #@patch.object(PredictStrategy, '__call__.chain')
    def test_predict_strategy(self, mock_celery):
        from kman_web.services.kman import PredictStrategy

        mock_celery.return_value.__name__ = 'mock_task'
        mock_celery.return_value.delay.return_value.id = '12345'
    
        strategy = PredictStrategy('predict')
        result_id = strategy(fasta)
        #mock_celery.return_value.delay.assert_called_once_with(fasta,
        #                                                         'predict')
         
        #eq_(result_id, '12345')
        pass

    
    
    
