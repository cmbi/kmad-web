

class Mutation(object):
    def __init__(self, sequence, position, mutant_aa):
        self.wild_sequence = sequence['seq']
        self.mutant_aa = mutant_aa
        # 0-based _position
        self.position = position - 1
        self.mutant_sequence = self._mutate()
        self.alignment_position = self._get_alignment_position(
            sequence, self.position)

    def _get_alignment_position(self, sequence, position):
        aligned = sequence['aligned']
        count = -1
        i = -1
        while i < len(aligned) - 1 and count < position:
            i += 1
            if aligned[i] != '-':
                count += 1
        return i

    def _mutate(self):
        tmp_seq = list(self.wild_sequence)
        tmp_seq[self.position] = self.mutant_aa
        return ''.join(tmp_seq)
