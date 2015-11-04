from mock import patch, PropertyMock
from nose.tools import eq_, ok_

from kmad_web.domain.features.user_features import UserFeaturesParser


def test_parse_features():
    usr = UserFeaturesParser()

    text_features = [
        {
            'featname': 'feat1', 'add_score': 2,
            'sequence_number': '2',
            'pattern': '',
            'positions': '7,6,8-9'
        },
        {
            'featname': 'feat1', 'add_score': 2,
            'sequence_number': '1',
            'pattern': '',
            'positions': '1'
        },
        {
            'featname': 'feat2', 'add_score': 2,
            'sequence_number': '2',
            'pattern': '',
            'positions': '7,6,8-9'
        }
    ]
    expected = 'feature_settings = \n  {\n' \
               + '  usr_features = ( \n' \
               + '{    name = "feat1";\n' \
               + '    tag = "";\n' \
               + '    add_score = 2;\n' \
               + '    subtract_score = "";\n' \
               + '    add_features = ("feat1");\n' \
               + '    add_tags = ();\n' \
               + '    add_exceptions = ();\n' \
               + '    subtract_features = ();\n' \
               + '    subtract_tags = ();\n' \
               + '    subtract_exceptions = ();\n' \
               + '    pattern = "";\n' \
               + '    positions = ( { seq = 2; pos = (7, 6, 8, 9); },\n' \
               + '{ seq = 1; pos = (1); }\n' \
               + ');\n' \
               + '}\n' \
               + '{    name = "feat2";\n' \
               + '    tag = "";\n' \
               + '    add_score = 2;\n' \
               + '    subtract_score = "";\n' \
               + '    add_features = ("feat2");\n' \
               + '    add_tags = ();\n' \
               + '    add_exceptions = ();\n' \
               + '    subtract_features = ();\n' \
               + '    subtract_tags = ();\n' \
               + '    subtract_exceptions = ();\n' \
               + '    pattern = "";\n' \
               + '    positions = ( { seq = 2; pos = (7, 6, 8, 9); }\n' \
               + ');\n' \
               + '}\n' \
               + ');\n' \
               + '};\n'
    expected_list = expected.splitlines()
    result_list = usr._parse(text_features).splitlines()
    for i in range(len(expected_list)):
        eq_(expected_list[i], result_list[i])


def test_remove_empty():
    usr = UserFeaturesParser()
    test = [{'1': [1, 2, 3], '2': None, '3': 5}]
    eq_(usr._remove_empty(test), [])
    test = [{'1': [1, 2, 3], '2': "test", '3': 5}]
    eq_(usr._remove_empty(test), test)
    test = [{'1': [], '2': "test", '3': 5}]
    eq_(usr._remove_empty(test), [])
    test = [{'1': [], '2': "test", '3': 5},
            {'1': [1, 2, 3], '2': "test", '3': 5}]
    eq_(usr._remove_empty(test), [{'1': [1, 2, 3], '2': "test", '3': 5}])


@patch('kmad_web.domain.features.user_features.tempfile.NamedTemporaryFile')
def test_write_conf(mock_temp):
    usr = UserFeaturesParser()
    text_features = [
        {
            'featname': 'feat1', 'add_score': 2,
            'sequence_number': '2',
            'pattern': '',
            'positions': '7,6,8-9'
        }
    ]
    tmp_name = 'tmp_name'
    type(mock_temp.return_value).name = PropertyMock(return_value=tmp_name)

    eq_(tmp_name, usr.write_conf_file(text_features))
    ok_(not usr.write_conf_file([]))
