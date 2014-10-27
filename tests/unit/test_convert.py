from mock import patch, mock_open

from nose.tools import eq_

from testdata.test_variables import *


@patch('kman_web.services.convert.elm_db')
@patch('kman_web.services.convert.tmp_fasta')
@patch('kman_web.services.convert.readFASTA')
@patch('kman_web.services.convert.findPhosphSites')
@patch('kman_web.services.convert.runNetPhos')
@patch('kman_web.services.convert.searchELM')
@patch('kman_web.services.convert.runPfamScan')
@patch('kman_web.services.convert.open', create=True)
def test_convert_to_7chars(mock_out_open, mock_run_pfam_scan, 
                           mock_search_elm, mock_run_netphos,
                           mock_find_phosph_sites, 
                           mock_read_fasta, mock_tmp_fasta,
                           mock_elm_db):

    filename = 'testdata/test.fasta'
    expected_outname = 'testdata/test.7c'

    mock_read_fasta.return_value = ['>1', 'SEQ']

    ## check: nothing to encode
    expected_data = '>1\nSAAAAAAEAAAAAAQAAAAAA\n## PROBABILITIES\nmotif index  probability\n'
    mock_run_pfam_scan.return_value = [[], []]
    mock_search_elm.return_value = [[], [], []]
    mock_run_netphos.return_value = []
    mock_find_phosph_sites.return_value = [[], [], [], [], [], [], []]
    mock_tmp_fasta.return_value = 'tmp_filename'
    mock_elm_db.return_value = 'elm_db'

    from kman_web.services.convert import convert_to_7chars
    
    convert_to_7chars(filename)

    mock_out_open.assert_called_once_with(expected_outname, 'w')
    handle = mock_out_open()
    handle.write.assert_called_once_with(expected_data)
    
    ## check: encoded domain
    mock_run_pfam_scan.return_value = [[[1,2]], ['domain']]
    expected_data = '>1\nSAaaAAAEAaaAAAQAAAAAA\n## PROBABILITIES\nmotif index  probability\n'
    handle.reset_mock()

    convert_to_7chars(filename)
    handle.write.assert_called_once_with(expected_data)

    ## check: encoded motif
    mock_run_pfam_scan.return_value = [[], []]
    mock_search_elm.return_value = [[[1,2]], ['MOTIF'], [0.9]]
    expected_data = '>1\nSAAAAaaEAAAAaaQAAAAAA\n## PROBABILITIES\nmotif index  probability\naa 0.9\n'
    handle.reset_mock()

    convert_to_7chars(filename)
    handle.write.assert_called_once_with(expected_data)

    ## check: encoded PTMs 
    mock_search_elm.return_value = [[], [], []]
    mock_find_phosph_sites.return_value = [[[1]], [[2]], [[3]], [], [], [], []]
    expected_data = '>1\nSAAAZAAEAAAVAAQAAARAA\n## PROBABILITIES\nmotif index  probability\n'
    handle.reset_mock()

    convert_to_7chars(filename)
    handle.write.assert_called_once_with(expected_data)


@patch('kman_web.services.convert.open', mock_open(read_data=open('testdata/TEST.dat').read()), create=True)
def test_get_uniprot_txt():
    with open('testdata/features.dat') as a:
        expected = a.read().splitlines()

    from kman_web.services.convert import get_uniprot_txt
    eq_(get_uniprot_txt('test_id'), expected)
    
    
    

    

    

