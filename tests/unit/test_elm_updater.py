from mock import patch
from nose.tools import eq_

from kmad_web.domain.updaters.elm import ElmUpdater


@patch('kmad_web.domain.updaters.elm.ElmUpdater._not_ok')
@patch('kmad_web.domain.updaters.elm.ElmUpdater._get_extended_go_terms')
@patch('kmad_web.domain.updaters.elm.json.dump')
@patch('kmad_web.services.elm.ElmService.get_all_classes')
def test_update(mock_get_all_classes, mock_json_dump,
                mock_get_extended_go_terms, mock_not_ok):
    with open('tests/unit/testdata/test_elm_classes.tsv') as a:
        test_classes = a.read()
    mock_get_all_classes.return_value = test_classes
    mock_get_extended_go_terms.return_value = ['goterm1', 'goterm2']
    mock_not_ok.return_value = False
    elm = ElmUpdater()
    elm._elmdb_path = 'tests/unit/testdata/test_db.txt'
    expected_json = {'CLV_C14_Caspase3-7': {'GO': ['goterm1', 'goterm2'],
                                            'pattern':
                                                '[DSTE][^P][^DEWHFYC]D[GSAN]',
                                            'class': "Caspase-3 and "
                                                     "Caspase-7 cleavage site",
                                            'probability': '0.00309374033071'}
                     }
    elm.update()
    eq_(list(mock_json_dump.call_args)[0][0], expected_json)
