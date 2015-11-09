from mock import patch
from nose.tools import eq_

from kmad_web.domain.sequences.annotator import SequencesAnnotator


@patch('kmad_web.domain.sequences.annotator.PfamFeatureProvider')
def test_annotate_domains(mock_pfam):
    sequences = [{'seq': 'SEQSEQ'}, {'seq': 'SEQSEQ'}]
    domains = [{'accession': 'TEST1'}]
    mock_pfam.return_value.get_domains.return_value = domains
    expected = [{'seq': 'SEQSEQ', 'domains': domains},
                {'seq': 'SEQSEQ', 'domains': domains}]

    seq_ann = SequencesAnnotator()
    seq_ann.sequences = sequences
    seq_ann._annotate_domains()
    eq_(expected, seq_ann.sequences)


@patch('kmad_web.domain.sequences.annotator.ElmFeatureProvider')
def test_annotate_motifs(mock_elm):
    go_terms = []
    sequences = [{'seq': 'SEQSEQ', 'id': 'TEST1'}, {'seq': 'SEQSEQ', 'id': ''}]
    motifs = [{'id': 'TEST1'}, {'id': 'TEST2'}]
    mock_elm.return_value.get_motif_instances.return_value = motifs
    filtered = [{'id': 'TEST1'}]
    mock_elm.return_value.filter_motifs.return_value = filtered
    expected = [{'seq': 'SEQSEQ', 'motifs': motifs, 'id': 'TEST1',
                 'motifs_filtered': filtered},
                {'seq': 'SEQSEQ', 'motifs': motifs, 'id': '',
                 'motifs_filtered': filtered}]

    seq_ann = SequencesAnnotator()
    seq_ann.sequences = sequences
    seq_ann._annotate_motifs(go_terms)
    eq_(expected, seq_ann.sequences)


@patch('kmad_web.domain.sequences.annotator.UniprotFeatureProvider')
@patch('kmad_web.domain.sequences.annotator.NetphosFeatureProvider')
def test_annotate_ptms(mock_netphos, mock_uniprot):
    sequences = [{'seq': 'SEQSEQ', 'id': 'seq_id'},
                 {'seq': 'SEQSEQ', 'id': ""}]
    ptms = [{'name': 'TEST1'}]
    phosph = [{'name': 'TEST2'}]
    all_p = phosph + ptms
    mock_uniprot.return_value.get_ptms.return_value = ptms
    mock_netphos.return_value.get_phosphorylations.return_value = phosph
    expected = [{'seq': 'SEQSEQ', 'id': 'seq_id', 'ptms': all_p},
                {'seq': 'SEQSEQ', 'id': '', 'ptms': phosph}]

    seq_ann = SequencesAnnotator()
    seq_ann.sequences = sequences
    seq_ann._annotate_ptms()
    eq_(expected, seq_ann.sequences)
