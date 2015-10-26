from mock import patch
from nose.tools import eq_

from kmad_web.domain.updaters.elm import ElmUpdater

@patch('kmad_web.domain.updaters.elm.json.dumps')
@patch('kmad_web.services.elm.ElmService.get_all_classes')
def test_update(mock_get_all_classes, mock_json_dumps):
    with open('tests/unit/testdata/test_elm_classes.tsv') as a:
        test_classes = a.read()
    mock_get_all_classes.return_value = test_classes

    elm = ElmUpdater()
    elm.update()
    expected_json = {'CLV_C14_Caspase3-7': {'GO': ['0001817', '0030154',
                                                   '0006915', '0008283',
                                                   '0006508', '0005829',
                                                   '0005634', '0005515',
                                                   '0004197'],
                                            'pattern':
                                                '[DSTE][^P][^DEWHFYC]D[GSAN]',
                                            'class': "Caspase-3 and " \
                                                     "Caspase-7 cleavage site",
                                            'probability': '0.00309374033071'}
                                            }
    eq_(list(mock_json_dumps.call_args)[0][0], expected_json)
