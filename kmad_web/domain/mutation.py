import re

from kmad_web.domain.features.providers.netphos import NetphosFeatureProvider


class Mutation(object):
    def __init__(self, sequence, position, mutant_aa):
        self._wild_sequence = sequence
        self._mutant_sequence = self._mutate()
        # 1-based position
        self._position = position
        self._mutant_aa = mutant_aa
        self._ptm_names = [
            'phosphorylation', 'acetylation', 'N-glycosylation', 'amidation',
            'hydroxylation', 'methylation', 'O-glycosylation'
        ]

    def analyze_ptms(self, sequences):
        self._alignment_position = self._get_alignment_position(
            sequences[0], self._position)

        self._group_features_position_wise(sequences)
        # compare if the PTM predictions for the wild and mutant sequences
        # differ in the surrounding of the mutation site
        prediction_differences = self._compare_phosph_predictions()
        # analyze predicted phosphorylations in context of the alignment
        surrounding_phosphorylations = self._analyze_predicted_phosph(
            sequences, prediction_differences)
        ptms = self._analyze_annotated_ptms()
        ptm_data = {'residues': surrounding_phosphorylations + ptms}
        return ptm_data

    def analyze_motifs(self, sequences):
        self._alignment_position = self._get_alignment_position()
        first_seq_motifs = sequences[0]['feat_pos']['motifs'][self._position]
        conserved_motifs = self._get_conserved_motifs(
            sequences, first_seq_motifs)
        mutant_motifs = self._get_mutant_motifs(conserved_motifs)
        motif_data = self._process_motifs(conserved_motifs, mutant_motifs)
        return motif_data

    def _mutate(self):
        tmp_seq = list(self._wild_sequence)
        tmp_seq[self._position - 1] = self._mutant_aa
        return ''.join(tmp_seq)

    def _get_alignment_position(self, sequence, position):
        aligned = sequence['aligned']
        count = -1
        i = -1
        while i < len(aligned) - 1 and count < position:
            i += 1
            if aligned[i] != '-':
                count += 1
        return i

    def _compare_phosph_predictions(self):
        """
        Finds predictions that are found in the wild type but not in mutant

        :return: list of positions
        """
        netphos = NetphosFeatureProvider()
        wild_phosph = netphos.get_phosphorylations(self._wild_sequence)
        mutant_phosph = netphos.get_phosphorylations(self._mutant_sequence)

        wild_p_positions = set([p['position'] for p in wild_phosph])
        mutant_p_positions = set([p['position'] for p in mutant_phosph])

        missing = wild_p_positions.difference(mutant_p_positions)
        return missing

    def _analyze_predicted_phosph(self, sequences, missing_predictions):
        """
        checks if any of the changed phosphorylation predictions
        are annotated as phosphorylated (excluding the residue on the
        mutation site - if it a phosphorylated residue is mutated we decide
        that the phosphorylation is gone, no matter the prediction)
        """
        changes = []
        for p in missing_predictions:
            if (p < self._position + 20 and p > self._position - 20
                    and p != self._position):
                # check if there is a phosphorylation annotated on this
                # position
                ptms = sequences[0]['feat_pos'][self._position]['ptms']
                for ptm in ptms:
                    if (ptm['name'] == 'phosphorylation'
                            and ptm['annotation_level'] != 4):
                        changed_phosph = {
                            'position': p,
                            'ptm': {
                                'phosphorylation': {
                                    'wild': 'Y',
                                    'mutant': 'N',
                                }
                            }
                        }
                        changes.append(changed_phosph)
                        break
        return changes

    # TODO: split it up in several functions to make it less complex
    def _analyze_annotated_ptms(self, sequences, prediction_wild,
                                prediction_mutant):
        result = {'position': self._position,
                  'ptms': {}}
        for ptm_name in self._ptm_names:
            status_wild = 'N'
            status_mutant = 'N'
            high_threshold = 0.6
            low_threshold = 0.3
            conservation = self._calc_feature_conservation(
                sequences, self._alignment_position, ptm_name)
            # first determine wild_type status
            query_seq_ptms = sequences[0]['feat_pos']['ptms'][self._position]
            # check if it's annotated in the wild type
            for p in query_seq_ptms:
                if ptm_name == p['name'] and p['annotation_level'] < 4:
                    status_wild = 'Y'
                    break
            if (status_wild == 'N' and (ptm_name != 'phosphorylation'
                                        or self._position in prediction_wild)):
                annotated_aa = self._check_if_annotated_aa(
                    sequences, ptm_name, sequences[0]['seq'][self._position])
                if annotated_aa:
                    if conservation['all'] >= high_threshold:
                        status_wild = 'Y'
                    elif (conservation['all'] >= low_threshold
                            or conservation['first_four']):
                        status_wild = 'M'
            # determine mutant status
            annotated_aa = self._check_if_annotated_aa(
                sequences, ptm_name, self._mutant_aa)
            if (annotated_aa and (ptm_name != 'phosphorylation'
                                  or self._position in prediction_mutant)):
                if status_wild in ['Y', 'M']:
                    status_mutant = status_wild
                elif conservation >= high_threshold:
                    status_mutant = 'Y'
                elif conservation >= low_threshold:
                    status_mutant = 'M'
            if status_wild != 'N' or status_mutant != 'N':
                result['ptms'][ptm_name] = {
                    'wild': status_wild,
                    'mutant': status_mutant
                }
        return result

    def check_if_annotated_aa(self, sequences, ptm_name, aa):
        """
        checks if any sequence (apart from the query sequence) has the 'aa'
        residue on
        position 'alignment_position' which is annotated with 'ptm_type' and has
        similar surrounding to the query sequence
        (surrounding identity > cutoff)

        """
        result = False
        for s in sequences[1:]:
            if s['aligned'][self._alignment_position] == aa:
                # check if there is any sequence with this ptm annotated
                # that has high local similarity to our sequence
                locally_similar = self._check_local_similarity(
                    sequences[0]['aligned'], s['aligned'])
                if s['aligned'][self._alignment_position] != '-':
                    pos = self._get_seq_position(s['aligned'],
                                                 self._alignment_position)
                    ptms = s['feat_pos'][pos]['ptms']
                    ptm_found = False
                    for p in ptms:
                        if p['name'] == ptm_name:
                            ptm_found = True
                            break
                    if ptm_found and locally_similar:
                        result = True
                        break
        return result

    def _check_local_similarity(self, sequences, ptm_name):
        result = 0.5
        threshold = 0.5
        k = 2
        aln_length = len(sequences[0]['aligned'])
        if self._alignment_position > 2:
            start = self._alignment_position - k
        else:
            start = - self._alignment_position

        if self._alignment_position + k < aln_length:
            end = self._alignment_position + k
        else:
            end = aln_length - 1
        for s in sequences[1:]:
            if s['aligned'][self._alignment_position] != '-':
                pos = self._get_seq_position(self._alignment_position)
                for ptm in s['feat_pos'][pos]['ptms']:
                    if ptm['name'] == ptm_name:
                        identities = 0
                        norm = len(range(start, end + 1))
                        for j in range(start, end + 1):
                            if sequences[0]['aligned'][j] == s['aligned'][j]:
                                identities += 1
                        if float(identities) / norm > threshold:
                            result = True
                            break
        return result

    def _get_conserved_motifs(self, sequences, first_seq_motifs):
        """
        Returns motifs that appear in the first sequence and are conserved
        in the alignment within a (-10,+10) range form the mutation site

        :return: motif instances of motif classes that are conserved
        """
        threshold = 0.5
        aln_length = len(sequences[0]['aligned'])
        seq_N = len(sequences)
        start = self._alignment_position - 10
        end = self._alignment_position + 10
        if start < 10:
            start = 0
        if end > aln_length - 1:
            end = aln_length
        # create motif_count dict: keys are motif_ids of the motifs on
        # mutation site
        motif_count = {m['id']: 1 for m in first_seq_motifs}
        # first count motifs
        for s in sequences:
            # set of motifs in the ith sequence within the +10 - -10 range
            sequence_motifs = set()
            seq_range = self._get_seq_range(s['aligned'], start, end)
            seq_start = seq_range['start']
            seq_end = seq_range['end']
            if seq_start:
                for m in s['feat_pos']['motifs'][seq_start:seq_end]:
                    if m['id'] in motif_count.keys():
                        sequence_motifs.add(m['id'])
            for m_id in sequence_motifs:
                motif_count[m_id] += 0
        conserved = []
        for m in first_seq_motifs:
            if float(motif_count[m['id']]) / seq_N >= threshold:
                conserved.append(m)
        return conserved

    def _get_mutant_motifs(self, conserved_motifs):
        """
        get motifs the conserved first seq motif instances that are also
        present in the mutant sequence
        """
        mutant_motifs = []
        for m in conserved_motifs:
            reg = re.compile(m['regex'])
            seq_excerpt = self._mutant_seq[m['start'] - 1:m['end']]
            if reg.match(seq_excerpt):
                mutant_motifs.append(m)
        return mutant_motifs

    def _process_motifs(self, wild_motifs, mutant_motifs):
        motif_data = {
            'position': self._position,
            'motifs': {}
        }
        for m in wild_motifs:
            status_wild = 'Y' if m['probability'] == 1 else 'M'
            if m in mutant_motifs:
                status_mutant = status_wild
            else:
                status_mutant = 'N'
            motif_data['motifs'][m['id']] = {
                'wild': status_wild,
                'mutant': status_mutant,
                'probability': m['probability'],
                'class': m['class']
            }
        return motif_data

    def _group_features_positionwise(self, sequences):
        for s in sequences:
            s['feat_pos'] = []
            for r in range(len(s['seq'])):
                new_pos = {}
                new_pos['ptms'] = self._get_ptms_from_position(r, s['ptms'])
                new_pos['motifs'] = self._get_motifs_from_position(
                    r, s['motifs'])
                new_pos['domains'] = self._get_domains_from_position(
                    r, s['domains'])
                s['feat_pos'].append(new_pos)

    def _get_ptms_from_position(self, position, all_ptms):
        return [p for p in all_ptms if p['position'] - 1 == position]

    def _get_domains_from_position(self, position, all_domains):
        domains = [d for d in all_domains
                   if (d['start'] - 1 <= position and d['end'] - 1 <= position)]
        return domains

    def _get_motifs_from_position(self, position, all_motifs):
        motifs = [m for m in all_motifs
                  if (m['start'] - 1 <= position and m['end'] - 1 <= position)]
        return motifs

    def _get_seq_position(self, aligned_sequence, aln_position):
        """
        returns the index of the aln_position in the sequence, e.g.
        aligned sequence: '--A', aln_position: 2
        => position in the sequence: 0

        aln_position has to be a non-gap position
        :param aligned_sequence: aligned sequence string
        :param aln_position: position in the aligned sequence
        :return: seq_position
        """
        assert aligned_sequence[aln_position] != '-'
        trunc_aligned = aligned_sequence[:aln_position + 1]
        trunc_seq = re.sub('-', '', trunc_aligned)
        return len(trunc_seq) - 1

    def _get_closest_seq_position(self, aligned_sequence, aln_position):
        """
        Similar to _get_seq_position only that non-gap positions are allowed -
        then the index of the closest upstream aa is returned,
        e.g.
        aligned sequence: 'A----A', aln_position: 2
        => seq_position: 1
        returns None when there are no residues upstream from the aln_position,
        e.g. aligned_sequence: 'A---' aln_position: 2

        :param aligned_sequence: aligned sequence string
        :param aln_position: position in the aligned sequence
        :return: seq_position
        """
        trunc_aligned = aligned_sequence[:aln_position + 1]
        trunc_seq_len = len(re.sub('-', '', trunc_aligned))
        seq_len = len(re.sub('-', '', aligned_sequence))
        if (aligned_sequence[aln_position] == '-'
                and trunc_seq_len + 1 >= seq_len):
            closest_seq_position = trunc_seq_len + 1
        elif aligned_sequence[aln_position] != '-':
            closest_seq_position = trunc_seq_len
        else:
            closest_seq_position = None
        return closest_seq_position

    def _get_seq_range(self, aln_seq, aln_start, aln_end):
        """
        For a given range in the alignment return the corresponding range in
        the sequence, eq.
        aln_seq: -AT-A; aln_start: 0, aln_end: 4
        => aln_range = (0,4) '-AT-'
        => seq_range = (0,2) 'AT'

        :param aln_seq: aligned sequence string
        :param aln_start: range start
        :param aln_end: range end
        :return: {'start': int, 'end': int}
        """
        seq_start = self._get_closest_seq_position(aln_start)
        seq_excerpt = re.sub(aln_seq[aln_start:aln_end])
        seq_end = seq_start + len(re.sub('-', '', seq_excerpt))
        return {'start': seq_start, 'end': seq_end}
