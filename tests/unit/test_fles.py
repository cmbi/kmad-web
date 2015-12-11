from nose.tools import eq_

from kmad_web.domain.fles import make_fles, parse_fles, fles2fasta


def test_parse_fles():
    test_fles = ">1\nTAAAAAAMAAAAAATAAAAAA\n" \
                ">2\n-AAAAAAMAAAAAATAAAAAA\n"

    expected = [
        {
            'header': '>1',
            'encoded_seq': 'TAAAAAAMAAAAAATAAAAAA'
        },
        {
            'header': '>2',
            'encoded_seq': '-AAAAAAMAAAAAATAAAAAA'
        },
    ]
    eq_(expected, parse_fles(test_fles))


def test_fles2fasta():
    test_fles = ">1\nTAAAAAAMAAAAAATAAAAAA\n" \
                ">2\n-AAAAAAMAAAAAATAAAAAA\n"

    expected = ">1\nTMT\n>2\n-MT"

    eq_(expected, fles2fasta(test_fles))


def test_make_fles():
    sequences = [
        {
            'header': '>1',
            'encoded_seq': 'SAAAAAAEAAAAAAQAAAAAA',
            'encoded_aligned': '-AAAAAASAAAAAAEAAAAAAQAAAAAA'
        },
        {
            'header': '>2',
            'encoded_seq': 'PAAAAAASAAAAAAEAAAAAA',
            'encoded_aligned': 'PAAAAAASAAAAAAEAAAAAA-AAAAAA'
        }
    ]
    expected = '>1\nSAAAAAAEAAAAAAQAAAAAA\n>2\nPAAAAAASAAAAAAEAAAAAA\n' \
               '## PROBABILITIES\n'
    motifs_dict = {}
    eq_(expected, make_fles(sequences, motifs_dict, aligned_mode=False))
    expected = '>1\n-AAAAAASAAAAAAEAAAAAAQAAAAAA\n' \
               '>2\nPAAAAAASAAAAAAEAAAAAA-AAAAAA\n' \
               '## PROBABILITIES\n'

    eq_(expected, make_fles(sequences, motifs_dict, aligned_mode=True))
