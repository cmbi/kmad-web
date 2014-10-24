from mock import patch
from nose.tools import eq_, ok_, raises

from kman_web.services.kman import (KmanStrategyFactory, PredictStrategy, 
                                    PredictAndAlignStrategy)


def test_kman_strategy_factory():
    strategy = KmanStrategyFactory.create('predict')
    ok_(isinstance(strategy, PredictStrategy))
    strategy = KmanStrategyFactory.create('predict_and_align')
    ok_(isinstance(strategy, PredictAndAlignStrategy))


@raises(ValueError)
def test_kman_strategy_factory_unexpected_output_type():
    KmanStrategyFactory.create('unexpected')



