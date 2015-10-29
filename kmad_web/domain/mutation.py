

class Mutation(object):
    def __init__(self, sequence, position, mutant_aa):
        self._wild_sequence = sequence
        self._mutant_sequence = self._mutate()
        # 1-based position
        self._position = position
        self._mutant_aa = mutant_aa

    # TODO: implement
    def analyze_ptms(self, sequences):
        self._alignment_position = self._get_alignment_position()
        # compare if the PTM predictions for the wild and mutant sequences
        # differ in the surrounding of the mutation site
        self._compare_phosph_predictions()
        # analyze predicted phosphorylations in context of the alignment
        self._analyze_predicted_phosph(sequences)
        self._analyze_annotated_ptms()
        pass

    # TODO: implement
    def analyze_motifs(self, sequences):
        self._alignment_position = self._get_alignment_position()
        pass

    def _mutate(self):
        tmp_seq = list(self._wild_sequence)
        tmp_seq[self._position - 1] = self._mutant_aa
        return ''.join(tmp_seq)

    # TODO: implement
    def _get_alignment_position(self):
        pass

    # TODO: implement
    def _compare_phosph_predictions(self):
        pass

    # TODO: implement
    def _analyze_predicted_phosph(sequences):
        pass

    # TODO: implement
    def _analyze_annotated_ptms():
        pass
