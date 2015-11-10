from kmad_web.domain.sequences.annotator import SequencesAnnotator


def test_annotate():
    with open('tests/integration/SIAL_HUMAN.fasta') as a:
        sequence1 = ''.join(a.read().splitlines()[1:])

    sequences = [
        {'header': 'header',
         'seq': sequence1,
         'id': 'P21815'}
    ]
    annotator = SequencesAnnotator()
    annotator.annotate(sequences)
