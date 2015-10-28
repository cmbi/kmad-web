import logging


from kmad_web.helpers import txtproc
from kmad_web.services import files
from kmad_web.domain.sequences.fasta import check_fasta, make_fasta


_log = logging.getLogger(__name__)


class KmadStrategyFactory(object):
    @classmethod
    def create(cls, output_type):
        if output_type == 'predict':
            return PredictStrategy(output_type)
        elif output_type in ['predict_and_align', 'hope']:
            return PredictAndAlignStrategy(output_type)
        elif output_type in ['align', 'refine']:
            return AlignStrategy(output_type)
        elif output_type == "annotate":
            return AnnotateStrategy(output_type)
        else:
            raise ValueError("Unexpected output type '{}'".format(output_type))


def MotifsStrategy(object):
    def __init__(self, sequence, position, mutant_aa):
        if not check_fasta(sequence):
            self._fasta_sequence = make_fasta(sequence)
        else:
            self._fasta_sequence = sequence
        self._position = position
        self._mutant_aa = mutant_aa
        self._feature_type = 'motifs'

    def __call__(self):
        from celery import chain
        from kmad_web.tasks import (run_blast, get_sequences_from_blast,
                                    create_fles, align, analyze_mutation,
                                    process_kmad_alignment)
        workflow = chain(
            run_blast.s(self._fasta_sequence),
            get_sequences_from_blast.s(),
            create_fles.s(),
            align.s(),
            process_kmad_alignment.s(),
            analyze_mutation.s(self._fasta_sequence, self._position,
                               self._mutant_aa, self._feature_type)
        )
        job = workflow()
        return job.id


def PtmsStrategy(object):
    def __init__(self, sequence, position, mutant_aa):
        if not check_fasta(sequence):
            self._fasta_sequence = make_fasta(sequence)
        else:
            self._fasta_sequence = sequence
        self._position = position
        self._mutant_aa = mutant_aa
        self._feature_type = 'ptms'

    def __call__(self):
        from celery import chain
        from kmad_web.tasks import (run_blast, get_sequences_from_blast,
                                    create_fles, align, analyze_mutation,
                                    parse_fles)
        workflow = chain(
            run_blast.s(self._fasta_sequence),
            get_sequences_from_blast.s(),
            create_fles.s(),
            align.s(),
            parse_fles.s(),
            analyze_mutation.s(self._fasta_sequence, self._position,
                               self._mutant_aa, self._feature_type)
        )
        job = workflow()
        return job.id


# TODO: change
class PredictStrategy(object):
    def __init__(self, output_type):
        self.output_type = output_type

    def __call__(self, fasta_seq, single_fasta_filename, multi_fasta_filename,
                 prediction_methods, multi_seq_input):
        from celery import chain, group
        from kmad_web.tasks import (query_d2p2, run_single_predictor,
                                    postprocess, get_seq)

        conffilename = ""
        tasks_to_run = [get_seq.s(fasta_seq)]
        for pred_name in prediction_methods:
            tasks_to_run += [run_single_predictor.s(single_fasta_filename,
                                                    pred_name)]
        workflow = chain(query_d2p2.s(single_fasta_filename, self.output_type,
                                      multi_seq_input),
                         group(tasks_to_run),
                         postprocess.s(single_fasta_filename,
                                       multi_fasta_filename,
                                       conffilename, self.output_type))
        return workflow


# TODO: remove
class PredictAndAlignStrategy(object):
    def __init__(self, output_type):
        self.output_type = output_type

    def __call__(self, fasta_seq, single_fasta_filename, multi_fasta_filename,
                 gap_opening_penalty, gap_extension_penalty,
                 end_gap_penalty, ptm_score, domain_score, motif_score,
                 prediction_methods, multi_seq_input, usr_features,
                 first_seq_gapped, alignment_method, filter_out_motifs):
        from kmad_web.tasks import (query_d2p2, align, run_single_predictor,
                                    postprocess, get_seq)
        from celery import chain, group

        usr_features = txtproc.remove_empty(usr_features)
        if usr_features:
            conffilename = files.write_conf_file(usr_features)
        else:
            conffilename = ""

        tasks_to_run = [get_seq.s(fasta_seq)]
        for pred_name in prediction_methods:
            tasks_to_run += [run_single_predictor.s(single_fasta_filename,
                                                    pred_name)]
        tasks_to_run += [align.s(multi_fasta_filename, gap_opening_penalty,
                                 gap_extension_penalty, end_gap_penalty,
                                 ptm_score, domain_score, motif_score,
                                 multi_seq_input, conffilename,
                                 self.output_type, first_seq_gapped,
                                 alignment_method, filter_out_motifs)]

        workflow = chain(query_d2p2.s(single_fasta_filename, self.output_type,
                                      multi_seq_input),
                         group(tasks_to_run),
                         postprocess.s(single_fasta_filename,
                                       multi_fasta_filename,
                                       conffilename, self.output_type))

        return workflow


# TODO: change
class AlignStrategy(object):
    def __init__(self, output_type):
        self.output_type = output_type

    def __call__(self, fasta_seq, single_fasta_filename, multi_fasta_filename,
                 gap_opening_penalty, gap_extension_penalty,
                 end_gap_penalty, ptm_score, domain_score, motif_score,
                 multi_seq_input, usr_features, output_type, first_seq_gapped,
                 alignment_method, filter_out_motifs):
        from kmad_web.tasks import (query_d2p2, align, postprocess, get_seq)
        from celery import chain, group

        usr_features = txtproc.remove_empty(usr_features)
        if usr_features:
            conffilename = files.write_conf_file(usr_features)
        else:
            conffilename = ""

        tasks_to_run = [get_seq.s(fasta_seq),
                        align.s(multi_fasta_filename, gap_opening_penalty,
                                gap_extension_penalty, end_gap_penalty,
                                ptm_score, domain_score, motif_score,
                                multi_seq_input, conffilename, output_type,
                                first_seq_gapped, alignment_method,
                                filter_out_motifs)]
        workflow = chain(query_d2p2.s(single_fasta_filename, self.output_type,
                                      multi_seq_input),
                         group(tasks_to_run),
                         postprocess.s(single_fasta_filename,
                                       multi_fasta_filename,
                                       conffilename, self.output_type))
        return workflow


# TODO: change
class AnnotateStrategy(object):
    def __init__(self, output_type):
        self.output_type = output_type

    def __call__(self, fasta_seq, single_fasta_filename, multi_fasta_filename):
        from kmad_web.tasks import (query_d2p2, annotate, postprocess, get_seq)
        from celery import chain, group
        fasta_seq = txtproc.process_fasta(fasta_seq)

        tasks_to_run = [get_seq.s(fasta_seq),
                        annotate.s(multi_fasta_filename)]
        workflow = chain(query_d2p2.s(single_fasta_filename, self.output_type,
                                      True),
                         group(tasks_to_run),
                         postprocess.s(single_fasta_filename,
                                       multi_fasta_filename,
                                       "dummyname", self.output_type))
        return workflow
