import logging

from kmad_web.services.elm import get_elm_instances

logging.basicConfig()
_log = logging.getLogger(__name__)


def obtain_motifs(uniprot_id, sequence, slim_classes, seq_goterms,
                  filter_motifs, predictions, seq_index, seqid_ok):
    _log.info("Obtaining motifs")
    # if seqid_ok:
    #     annotated = get_elm_instances(uniprotID)
    # else:
    #     annotated = [[], [], []]
    # predicted = get_predicted_motifs(sequence, slims_all_classes, seq_go_terms,
    #                                  filter_motifs, predictions, seq_index)

    # motif_data = process_result
    # limits = annotated[0] + predicted[0]
    # elms_ids = annotated[1] + predicted[1]
    # probabilities = annotated[2] + predicted[2]

    # limits, elms_ids, probabilities = filter_out_overlapping(limits,
    #                                                          elms_ids,
    #                                                          probabilities)
    # return [limits, elms_ids, probabilities, annotated]
    pass
