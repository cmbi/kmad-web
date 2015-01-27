import glob
import json
import logging
import os
import subprocess
import urllib2

from celery import current_app as celery_app

from kman_web import paths
from kman_web.services.txtproc import (preprocess, process_alignment,
                                       find_seqid_blast, process_d2p2)
from kman_web.services.consensus import (find_consensus_disorder,
                                         filter_out_short_stretches)
from kman_web.services.convert import convert_to_7chars
from kman_web.services.files import (get_fasta_from_blast,
                                     disopred_outfilename,
                                     predisorder_outfilename,
                                     psipred_outfilename)


logging.basicConfig()
_log = logging.getLogger(__name__)


@celery_app.task
def postprocess(result, filename, output_type):
    # process result and remove tmp files
    _log.debug("Postprocessing the results")
    prefix = filename[0:14]
    if glob.glob('%s*' % prefix):
        os.system('rm %s*' % prefix)    # pragma: no cover
    prefix = prefix[5:]
    if glob.glob('%s*' % prefix):
        os.system('rm %s*' % prefix)    # pragma: no cover

    # If the results are not form the d2p2 database, then process them
    # (find consensus, and filter out short stretches)
    if (output_type == 'predict_and_align'
            and not (len(result) == 3 and result[1][0] == 'D2P2')):
        # first element is the sequence, last element is the alignement
        consensus = find_consensus_disorder(result[1:-1])
        result = result[:-1] + [consensus] + [result[-1]]
        # so that the alignment stays at the very end
        result = result[:-1] \
            + [filter_out_short_stretches(consensus[1])] \
            + [result[-1]]
    elif (output_type == 'predict'
          and not (len(result) == 2 and result[1][0] == 'D2P2')):
        consensus = find_consensus_disorder(result[1:])
        result += [consensus]
        result += [filter_out_short_stretches(consensus[1])]
    # else: output_type = 'align' -> then there is no need to change the result
    return result


@celery_app.task
def run_single_predictor(prev_result, fasta_file, pred_name):
    _log.debug("Run single predictor")
    if prev_result[0]:
        return prev_result[1]
    else:
        if pred_name == "dummy":    # pragma: no cover
            sequence = open(fasta_file).readlines()[1:]
            sequence = [i.rstrip("\n") for i in sequence]
            sequence = ''.join(sequence)
            data = ["dummy", [0 for i in sequence]]
        else:
            if pred_name == "spine":
                tmp_name = fasta_file.split('/')[-1].split('.')[0]
                tmp_path = '/'.join(fasta_file.split("/")[:-1])
                method = paths.SPINE_DIR+"/bin/run_spine-d"
                args = [method, tmp_path, tmp_name]
                out_file = paths.SPINE_OUTPUT_DIR+tmp_name+".spd"
            elif pred_name == "disopred":
                method = paths.DISOPRED_PATH
                args = [method, fasta_file]
                out_file = disopred_outfilename(fasta_file)
            elif pred_name == "predisorder":
                method = paths.PREDISORDER_PATH
                out_file = predisorder_outfilename(fasta_file)
                args = [method, fasta_file, out_file]
            elif pred_name == "psipred":
                method = paths.PSIPRED_PATH
                out_file = psipred_outfilename(fasta_file)
                args = [method, fasta_file]
            _log.debug("Running command '{}'".format(args))
            subprocess.call(args)
            with open(out_file) as f:
                data = f.read()
            data = preprocess(data, pred_name)
        return data


@celery_app.task
def align(d2p2, filename, gap_opening_penalty, gap_extension_penalty,
          end_gap_penalty, ptm_score, domain_score, motif_score):
    # blast result file already created in "query_d2p2"
    out_blast = filename.split(".")[0]+".blastp"
    fastafile = get_fasta_from_blast(out_blast, filename)  # fasta filename

    toalign = convert_to_7chars(fastafile)  # .7c filename
    codon_length = 7

    al_outfile = "%s_al" % toalign
    args = ["kman", "-i", toalign,
            "-o", toalign, "-g", str(gap_opening_penalty),
            "-n", str(end_gap_penalty), "-e", str(gap_extension_penalty),
            "-p", str(ptm_score), "-d", str(domain_score),
            "--out-encoded",
            "-m", str(motif_score), "-c", str(codon_length)]
    _log.debug("KMAN: {}".format(subprocess.list2cmdline(args)))
    subprocess.call(args)
    with open(fastafile.split('.')[0] + '.map') as a:
        feature_codemap = a.read().splitlines()
    alignment_encoded = open(al_outfile).read().encode('ascii', errors='ignore')
    alignment_processed = process_alignment(alignment_encoded, codon_length)
    result = alignment_processed + [feature_codemap]
    # return alignment_processed
    return result


@celery_app.task
def get_seq(d2p2, fasta_file):
    return fasta_file.splitlines()[1].encode('ascii', errors='ignore')


@celery_app.task
def query_d2p2(filename, output_type):
    found_it = False
    prediction = []
    out_blast = filename.split(".")[0]+".blastp"
    args = ["blastp", "-query", filename, "-evalue", "1e-5",
            "-num_threads", "15", "-db", paths.SWISSPROT_DB,
            "-out", out_blast]
    subprocess.call(args)
    if output_type != 'align':
        [found_it, seq_id] = find_seqid_blast(out_blast)
        if found_it:
            data = 'seqids=["%s"]' % seq_id
            request = urllib2.Request('http://d2p2.pro/api/seqid', data)
            response = json.loads(urllib2.urlopen(request).read())
            if response[seq_id]:
                pred_result = response[seq_id][0][2]['disorder']['consensus']
                prediction = process_d2p2(pred_result)
            else:
                found_it = False
    return [found_it, prediction]


def get_task(output_type):
    """
    Get the task for the given output_type.

    If the output_type is not allowed, a ValueError is raised.
    """
    _log.info("Getting task for output '{}'".format(output_type))
    if output_type in ['predict', 'predict_and_align', 'align']:
        task = postprocess
    else:
        raise ValueError("Unexpected output_type '{}'".format(output_type))

    _log.debug("Got task '{}'".format(task.__name__))
    return task
