from mock import patch, Mock
from nose.tools import eq_, ok_, assert_raises

from kmad_web.parsers.phosphosite import PhosphositeParser
from kmad_web.parsers.types import ParserError


@patch('kmad_web.parsers.phosphosite.PhosphositeParser.parse_db')
@patch('kmad_web.parsers.phosphosite.os.path.exists')
def test_get_ptm_sites_success(mock_path_exists, mock_parse_db):
    path = "/home/joanna/data/phosphosite"
    ptm_type = "phosph"
    uniprot_id = "P28360"
    mock_path_exists.return_value = True
    psite = PhosphositeParser(path)
    psite.get_ptm_sites(uniprot_id, ptm_type)
    ok_(mock_parse_db.called)


@patch('kmad_web.parsers.phosphosite.os.path.exists')
def test_get_ptm_sites_failure(mock_path_exists):
    path = "/home/joanna/data/phosphosite"
    ptm_type = "phosph"
    uniprot_id = "P28360"
    mock_path_exists.return_value = False
    psite = PhosphositeParser(path)
    assert_raises(ParserError, psite.get_ptm_sites, uniprot_id, ptm_type)


def test_parse_db():
    test_db = "14-3-3 epsilon	P62259	Ywhae		S233-p	14569200	mouse" \
              "29.17	14-3-3	DNLTLWTsDMQGDGE		3\n" \
              "14-3-3 sigma	P31947	SFN	1p36.11	S186-p	456054	human	27.77" \
              "14-3-3	FHYEIANsPEEAISL	3\n"
    test_id = "P62259"
    expected_result = ["233"]
    psite = PhosphositeParser()
    eq_(psite.parse_db(test_db, test_id), expected_result)
