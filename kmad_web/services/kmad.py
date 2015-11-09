import logging
import tempfile


from kmad_web.domain.features.user_features import UserFeaturesParser
from kmad_web.domain.sequences.fasta import (check_fasta, make_fasta,
                                             parse_fasta)


_log = logging.getLogger(__name__)


class MotifsStrategy(object):
    def __init__(self, sequence, position, mutant_aa):
        if not check_fasta(sequence):
            self._fasta_sequence = make_fasta(sequence)
            self._raw_sequence = sequence
        else:
            self._fasta_sequence = sequence
            self._raw_sequence = parse_fasta(sequence)[0]['seq']
        self._position = position
        self._mutant_aa = mutant_aa
        self._feature_type = 'motifs'
        self._gop = '-12'
        self._gep = '-1.2'
        self._egp = '-1.2'
        self._ptm_score = '10'
        self._motif_score = '4'
        self._domain_score = '4'
        self._full_ungapped = 'True'

    def __call__(self):
        from celery import chain
        from kmad_web.tasks import (run_blast, get_sequences_from_blast,
                                    create_fles, run_kmad, analyze_motifs,
                                    process_kmad_alignment)
        workflow = chain(
            run_blast.s(self._fasta_sequence),
            get_sequences_from_blast.s(),
            create_fles.s(),
            run_kmad.s(self._gop, self._gep, self._egp, self._ptm_score,
                       self._domain_score, self._motif_score,
                       full_ungapped=self._full_ungapped),
            process_kmad_alignment.s(),
            analyze_motifs.s(self._raw_sequence, self._position,
                             self._mutant_aa)
        )
        job = workflow()
        return job.id


class PtmsStrategy(object):
    def __init__(self, sequence, position, mutant_aa):
        if not check_fasta(sequence):
            self._fasta_sequence = make_fasta(sequence)
        else:
            self._fasta_sequence = sequence
        self._position = position
        self._mutant_aa = mutant_aa
        self._feature_type = 'ptms'
        self._gop = '-12'
        self._gep = '-1.2'
        self._egp = '-1.2'
        self._ptm_score = '10'
        self._motif_score = '4'
        self._domain_score = '4'
        self._full_ungapped = 'True'

    def __call__(self):
        from celery import chain
        from kmad_web.tasks import (run_blast, get_sequences_from_blast,
                                    create_fles, run_kmad, analyze_ptms,
                                    process_kmad_alignment)
        workflow = chain(
            run_blast.s(self._fasta_sequence),
            get_sequences_from_blast.s(),
            create_fles.s(),
            run_kmad.s(self._gop, self._gep, self._egp, self._ptm_score,
                       self._domain_score, self._motif_score,
                       full_ungapped=self._full_ungapped),
            process_kmad_alignment.s(),
            analyze_ptms.s(self._fasta_sequence, self._position,
                           self._mutant_aa)
        )
        job = workflow()
        return job.id


class PredictStrategy(object):
    def __init__(self, fasta_sequence, prediction_methods):
        self._fasta_sequence = fasta_sequence
        self._prediction_methods = prediction_methods

    def __call__(self):
        from celery import chain, group
        from kmad_web.tasks import (run_blast, query_d2p2, run_single_predictor,
                                    process_prediction_results)

        tmp_file = tempfile.NamedTemporaryFile(suffix=".fasta", delete=False)
        with tmp_file as f:
            f.write(self._fasta_sequence)

        if 'd2p2' in self._prediction_methods:
            prediction_tasks = [
                chain(
                    run_blast.s(self._fasta_sequence),
                    query_d2p2.s()
                )
            ]
        else:
            prediction_tasks = []
        for pred_name in self._prediction_methods:
            if pred_name != 'd2p2':
                prediction_tasks += [run_single_predictor.s(tmp_file.name,
                                                            pred_name)]
        workflow = chain(
            group(prediction_tasks),
            process_prediction_results.s(self._fasta_sequence)
        )
        job = workflow()
        return job.id


class AlignStrategy(object):
    def __init__(self, sequence_data, gop, gep, egp, ptm_score,
                 domain_score, motif_score, gapped, usr_features):
        self._fasta = make_fasta(sequence_data)
        self._gop = gop
        self._gep = gep
        self._egp = egp
        self._ptm_score = ptm_score
        self._motif_score = motif_score
        self._domain_score = domain_score
        self._gapped = gapped
        self._usr_features = usr_features
        self._multi_fasta = sequence_data.count('>') > 1

    def __call__(self):

        from kmad_web.tasks import (create_fles, get_sequences_from_blast,
                                    run_kmad, run_blast,
                                    process_kmad_alignment)
        from celery import chain

        user_feat_parser = UserFeaturesParser()
        config_path = user_feat_parser.write_conf_file(self._usr_features)

        if self._multi_fasta:
            sequences = parse_fasta(self._fasta)
            tasks = [create_fles.s(sequences)]
        else:
            tasks = [run_blast.s(self._fasta),
                     get_sequences_from_blast.s(),
                     create_fles.s()]
        tasks.extend([
            run_kmad.s(self._gop, self._gep, self._egp, self._ptm_score,
                       self._domain_score, self._motif_score, config_path,
                       self._gapped),
            process_kmad_alignment.s()
        ])
        workflow = chain(tasks)
        job = workflow()
        return job.id


class RefineStrategy(object):
    def __init__(self, sequence_data, gop, gep, egp, ptm_score,
                 domain_score, motif_score, gapped, usr_features,
                 alignment_method=None):
        self._fasta = make_fasta(sequence_data)
        self._gop = gop
        self._gep = gep
        self._egp = egp
        self._ptm_score = ptm_score
        self._motif_score = motif_score
        self._domain_score = domain_score
        self._gapped = gapped
        self._usr_features = usr_features
        self._multi_fasta = sequence_data.count('>') > 1
        self._alignment_method = alignment_method

    def __call__(self):

        from kmad_web.tasks import (create_fles, get_sequences_from_blast,
                                    run_kmad, run_blast, prealign,
                                    process_kmad_alignment)
        from celery import chain

        user_feat_parser = UserFeaturesParser()
        config_path = user_feat_parser.write_conf_file(self._usr_features)

        if not self._multi_fasta and self._alignment_method:
            tasks = [
                run_blast.s(self._fasta),
                get_sequences_from_blast.s(),
                prealign.s(self._alignment_method),
                create_fles.s(aligned_mode=True)
            ]
        elif self._multi_fasta and self._alignment_method:
            tasks = [
                prealign.s(self._alignment_method),
                create_fles.s(aligned_mode=True)
            ]
        elif self._multi_fasta and not self._alignment_method:
            sequences = parse_fasta(self._fasta)
            tasks = [create_fles.s(sequences, aligned_mode=True)]
        else:
            raise RuntimeError("sequence data holds a single sequence, but no"
                               " prealignment method is specified")
        tasks.extend([
            run_kmad.s(self._gop, self._gep, self._egp, self._ptm_score,
                       self._domain_score, self._motif_score, config_path,
                       self._gapped, refine=True),
            process_kmad_alignment.s()
        ])
        workflow = chain(tasks)
        job = workflow()
        return job.id


class AnnotateStrategy(object):
    def __init__(self, sequences):
        self._sequences = sequences

    def __call__(self):
        from kmad_web.tasks import annotate

        job = annotate.delay(self._sequences)
        return job.id
