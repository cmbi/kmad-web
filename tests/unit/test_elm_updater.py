from mock import patch, PropertyMock
from nose.tools import eq_, with_setup

from kmad_web.domain.updaters.elm import ElmUpdater
from kmad_web.services.helpers.cache import cache_manager as cm


def setup():
    cm.load_config({
        'redis': {'redis.backend': 'dogpile.cache.null'}
    })


def teardown():
    cm.reset()


@patch('kmad_web.domain.updaters.elm.ElmUpdater._not_ok')
@patch('kmad_web.domain.updaters.elm.ElmUpdater._get_extended_go_terms')
@patch('kmad_web.domain.updaters.elm.json.dump')
@patch('kmad_web.services.elm.ElmService.get_all_classes')
@with_setup(setup, teardown)
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
                                            'description': "Caspase-3 and "
                                                "Caspase-7 cleavage site",
                                            'class': "Caspase cleavage motif",
                                            'probability': '0.00309374033071'}
                     }
    elm.update()
    eq_(list(mock_json_dump.call_args)[0][0], expected_json)


@patch('kmad_web.domain.updaters.elm.ElmService.get_motif_go_terms')
@patch('kmad_web.domain.updaters.elm.GoProvider')
@with_setup(setup, teardown)
def test_get_extended_go_terms(mock_go, mock_get_go):

    from kmad_web.domain.updaters.elm import ElmUpdater

    elm = ElmUpdater()
    mock_get_go.return_value = set(['GO:0000001'])
    parents = set(['GO:0000101', 'GO:0000102'])
    children = set(['GO:0000111', 'GO:0000112'])
    type(mock_go.return_value).children = PropertyMock(return_value=children)
    type(mock_go.return_value).parents = PropertyMock(return_value=parents)
    expected = set(['GO:0000001', 'GO:0000101', 'GO:0000102',
                    'GO:0000111', 'GO:0000112'])
    eq_(expected, elm._get_extended_go_terms("motif_id"))
