from nose.tools import eq_, assert_raises
import kmad_web.domain.sequences.fasta as f


def test_parse_fasta():
    fasta_file = '>1\nSEQ\nSEQ\n>2\nSEQ\nSEQ\n'
    expected = [{'header': '>1',
                 'seq': 'SEQSEQ'},
                {'header': '>2',
                 'seq': 'SEQSEQ'}
                ]

    eq_(expected, f.parse_fasta(fasta_file))


def test_make_fasta():
    seq = "SEQ"
    eq_(">sequence\nSEQ\n", f.make_fasta(seq))
    seq = ">1\nSEQ"
    eq_(">1\nSEQ", f.make_fasta(seq))
    seq = ">1\nSEQ\nSEQ"
    eq_(">1\nSEQ\nSEQ", f.make_fasta(seq))
    seq = "SEQ\nSEQ"
    eq_(">sequence\nSEQSEQ\n", f.make_fasta(seq))

    seq = "SE*"
    assert_raises(RuntimeError, f.make_fasta, seq)
    seq = ">1\nSEQ\nSE*\nSEQ"
    assert_raises(RuntimeError, f.make_fasta, seq)
    seq = ">1\nSEQ\n>1\nSE#\n>1\nSEQ"
    assert_raises(RuntimeError, f.make_fasta, seq)


def test_get_first_seq():
    multi_fasta = ">1\nSEQ\nSEQ\n>2\nSEQ"
    expected = ">1\nSEQSEQ"
    eq_(expected, f.get_first_seq(multi_fasta))
