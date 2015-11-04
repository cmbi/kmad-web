from nose.tools import eq_

from kmad_web.domain.disorder_prediction.processor import PredictionProcessor


def test_process_prediction():
    p = PredictionProcessor()

    with open('tests/unit/testdata/test.spine') as a:
        prediction_lines = a.read().splitlines()
    expected = [0, 2, 2]
    eq_(expected, p.process_prediction(prediction_lines, 'spine'))

    with open('tests/unit/testdata/test.disopred') as a:
        prediction_lines = a.read().splitlines()
    expected = [0, 2, 2]
    eq_(expected, p.process_prediction(prediction_lines, 'disopred'))

    with open('tests/unit/testdata/test.psipred') as a:
        prediction_lines = a.read().splitlines()
    expected = [0, 2, 2]
    eq_(expected, p.process_prediction(prediction_lines, 'psipred'))

    with open('tests/unit/testdata/test.predisorder') as a:
        prediction_lines = a.read().splitlines()
    expected = [0, 2, 2]
    eq_(expected, p.process_prediction(prediction_lines, 'predisorder'))

    with open('tests/unit/testdata/test.globplot') as a:
        prediction_lines = a.read().splitlines()
    expected = [0, 2, 2]
    eq_(expected, p.process_prediction(prediction_lines, 'globplot'))

    with open('tests/unit/testdata/test.iupred') as a:
        prediction_lines = a.read().splitlines()
    expected = [0, 2, 2]
    eq_(expected, p.process_prediction(prediction_lines, 'iupred'))

    prediction = [0, 5, 9]
    expected = [0, 1, 2]
    eq_(expected, p.process_prediction(prediction, 'd2p2'))


def test_get_consensus_disorder():
    predictions = {
        'method1': [0, 2, 0],
        'method2': [0, 2, 0],
        'method3': [2, 2, 0],
        'method4': [2, 0, 2],
    }

    expected = [1, 2, 0]

    p = PredictionProcessor()
    eq_(expected, p.get_consensus_disorder(predictions))


def test_filter_out_short_stretches():
    p = PredictionProcessor()
    test_data = [0, 0, 1, 0, 0, 0, 2, 1, 1, 1, 1, 1, 0]
    expected = [0, 0, 0, 0, 0, 0, 2, 1, 1, 1, 1, 1, 1]

    eq_(expected, p.filter_out_short_stretches(test_data))
    test_data = [0, 0, 1, 0, 0, 0, 2, 1, 1, 1, 1, 1, 1]
    expected = [0, 0, 0, 0, 0, 0, 2, 1, 1, 1, 1, 1, 1]

    eq_(expected, p.filter_out_short_stretches(test_data))
