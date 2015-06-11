import json
import logging
import os
import subprocess
import re
import tempfile
import urllib2

from celery import current_app as celery_app

from kmad_web import paths
from kmad_web.services import files
from kmad_web.services import mutation_analysis as ma
from kmad_web.services.txtproc import (preprocess, process_alignment,
                                       find_seqid_blast, process_d2p2)
from kmad_web.services.consensus import (find_consensus_disorder,
                                         filter_out_short_stretches)
from kmad_web.services.convert import convert_to_7chars, run_netphos
from kmad_web.services.files import (get_fasta_from_blast,
                                     disopred_outfilename,
                                     predisorder_outfilename,
                                     psipred_outfilename)
from kmad_web.services import update_elm as elm


logging.basicConfig()
_log = logging.getLogger(__name__)


@celery_app.task
def postprocess(result, single_filename, multi_filename, conffilename,
                output_type):
    # process result and remove tmp files
    _log.debug("Postprocessing the results")
    files.remove_files(single_filename)
    files.remove_files(multi_filename)
    if conffilename:
        files.remove_files(conffilename)

    # If the results are not from the d2p2 database and from more than one
    # method, then process them
    # (find consensus, and filter out short stretches)
    if (output_type == 'predict_and_align'
            and (len(result) > 3 and not result[1][0] == 'D2P2')):
        # first element is the sequence, last element is the alignement
        consensus = find_consensus_disorder(result[1:-1])
        result = result[:-1] + [consensus] + [result[-1]]
        # so that the alignment stays at the very end
        result = result[:-1] \
            + [filter_out_short_stretches(consensus[1])] \
            + [result[-1]]
    elif (output_type == 'predict'
          and (len(result) > 2 and not result[1][0] == 'D2P2')):
        consensus = find_consensus_disorder(result[1:])
        result += [consensus]
        result += [filter_out_short_stretches(consensus[1])]
    elif output_type == 'predict_and_align':
        result = [result[0]] + result[-2:]
    elif output_type == 'predict':
        result = result[:2]
    # else: output_type = 'align' or 'annotate' -> then there is no need to
    # change the result
    return result


@celery_app.task
def run_single_predictor(prev_result, fasta_file, pred_name):
    _log.debug("Run single predictor: {}".format(pred_name))
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
                out_file = paths.SPINE_OUTPUT_DIR + tmp_name + ".spd"
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
            elif pred_name == 'globplot':
                method = paths.GLOBPLOT_PATH
                out_file = fasta_file + ".gplot"
                args = [method, '10', '8', '75', '8', '8',
                        fasta_file, '>', out_file]
                _log.debug(args)
            try:
                if pred_name == 'globplot':
                    # data = run_globplot(fasta_file)
                    data = subprocess.check_output(args)
                else:
                    _log.info("Ran command: {}".format(
                        subprocess.list2cmdline(args)))
                    subprocess.call(args)
                    _log.info("out file name: {}; exists: {}".format(out_file,
                              os.path.exists(out_file)))
                    if os.path.exists(out_file):
                        with open(out_file) as f:
                            data = f.read()
                    else:
                        _log.info(
                            "Ouput file {} doesn't exist".format(out_file))
                data = preprocess(data, pred_name)
            except (subprocess.CalledProcessError, OSError) as e:
                _log.error("Error: {}".format(e))
        return data


@celery_app.task
def align(d2p2, filename, gap_opening_penalty, gap_extension_penalty,
          end_gap_penalty, ptm_score, domain_score, motif_score,
          multi_seq_input, conffilename, output_type, first_seq_gapped):
    # blast result file already created in "query_d2p2"
    if not multi_seq_input:
        out_blast = filename.split(".")[0]+".blastp"
        # fasta filename
        fastafile, blast_success = get_fasta_from_blast(out_blast, filename)
        _log.debug("BLAST success: {}".format(blast_success))
    else:
        fastafile = filename
    if multi_seq_input or blast_success:
        convert_result = convert_to_7chars(fastafile)  # .7c filename
        toalign = convert_result['filename']
        annotated_motifs = convert_result['annotated_motifs']
        codon_length = 7

        al_outfile = "%s_al" % toalign
        args = ["kmad", "-i", toalign,
                "-o", toalign, "-g", str(gap_opening_penalty),
                "-n", str(end_gap_penalty), "-e", str(gap_extension_penalty),
                "-p", str(ptm_score), "-d", str(domain_score),
                "--out-encoded", "--opt",
                "-m", str(motif_score), "-c", str(codon_length)]
        if output_type == "refine":
            args.append("--refine")
        if conffilename:
            args.extend(["--conf", conffilename])
        if first_seq_gapped == "gapped":
            args.append("--gapped")
        _log.debug("Running KMAD: {}".format(subprocess.list2cmdline(args)))
        subprocess.call(args)

        with open(fastafile.split('.')[0] + '.map') as a:
            feature_codemap = a.read().splitlines()

        motifs = [[i.split()[0].split('_')[1]] + i.split()[1:]
                  for i in feature_codemap if i.startswith('motif')]

        domains = [[i.split()[0].split('_')[1], i.split()[1]]
                   for i in feature_codemap if i.startswith('domain')]

        feature_codemap = {'motifs': motifs, 'domains': domains}

        alignment_encoded = open(al_outfile).read().encode('ascii',
                                                           errors='ignore')
        alignment_processed = process_alignment(alignment_encoded, codon_length)
        alignments = alignment_processed + [feature_codemap]
        _log.debug("feature codemap: {}".format(feature_codemap))
        result = {'alignments': alignments,
                  'annotated_motifs': annotated_motifs}
    else:
        result = {'alignments': [[], [], [], []],
                  'annotated_motifs': []}
    _log.debug("Finished alignment")
    return result


@celery_app.task
def annotate(d2p2, filename):
    convert_result = convert_to_7chars(filename)
    encoded_filename = convert_result['filename']
    with open(filename.split('.')[0] + '.map') as a:
        feature_codemap = a.read().splitlines()
    # motifs = [i.split() for i in feature_codemap if i.startswith('motif')]
    # domains = [i.split() for i in feature_codemap if i.startswith('domain')]
    motifs = [[i.split()[0].split('_')[1]] + i.split()[1:]
              for i in feature_codemap if i.startswith('motif')]

    domains = [[i.split()[0].split('_')[1], i.split()[1]]
               for i in feature_codemap if i.startswith('domain')]

    feature_codemap = {'motifs': motifs, 'domains': domains}

    encoded = open(encoded_filename).read().encode('ascii',
                                                   errors='ignore')
    codon_length = 7
    processed = process_alignment(encoded, codon_length)
    alignments = processed + [feature_codemap]
    result = {'alignments': alignments,
              'annotated_motifs': convert_result['annotated_motifs']}
    return result


@celery_app.task
def get_seq(d2p2, fasta_file):
    return fasta_file.splitlines()[1].encode('ascii', errors='ignore')


@celery_app.task
def run_blast(filename):
    out_blast = filename.split(".")[0]+".blastp"
    args = ["blastp", "-query", filename, "-evalue", "1e-5",
            "-num_threads", "15", "-db", paths.SWISSPROT_DB,
            "-out", out_blast, '-outfmt', '10']
    try:
        subprocess.call(args)
    except subprocess.CalledProcessError as e:
        _log.error("Error: {}".format(e.output))


@celery_app.task
def query_d2p2(filename, output_type, multi_seq_input):
    found_it = False
    prediction = []
    if not (multi_seq_input and output_type == 'align'):
        out_blast = filename.split(".")[0]+".blastp"
        # args = ["blastp", "-query", filename, "-evalue", "1e-5",
        #         "-num_threads", "15", "-db", paths.SWISSPROT_DB,
        #         "-out", out_blast, '-outfmt', '10']
        # try:
        #     subprocess.call(args)
        # except subprocess.CalledProcessError as e:
        #     _log.error("Error: {}".format(e.output))
        # if output_type != 'align':
        if os.path.exists(out_blast):
            [found_it, seq_id] = find_seqid_blast(out_blast)
            if found_it:
                data = 'seqids=["%s"]' % seq_id
                request = urllib2.Request('http://d2p2.pro/api/seqid', data)
                response = json.loads(urllib2.urlopen(request).read())
                if response[seq_id]:
                    pred_result = \
                        response[seq_id][0][2]['disorder']['consensus']
                    prediction = process_d2p2(pred_result)
                else:
                    found_it = False
    return [found_it, prediction]


# mutation_site - 1-based position
@celery_app.task
def analyze_mutation(processed_result, mutation_site, new_aa,
                     wild_seq_filename):
    mutation_site_0 = mutation_site - 1  # 0-based mutation site position
    wild_seq = processed_result[0]

    disorder_prediction = processed_result[-2]  # filtered consensus
    encoded_alignment = processed_result[-1]['alignments'][2]
    proc_alignment = processed_result[-1]['alignments'][1]
    feature_codemap = processed_result[-1]['alignments'][3]

    annotated_motifs = processed_result[-1]['annotated_motifs']

    mutant_seq = ma.create_mutant_sequence(wild_seq, mutation_site_0, new_aa)
    mutant_seq_file = tempfile.NamedTemporaryFile(suffix=".fasta", delete=False)
    with mutant_seq_file as f:
        f.write(mutant_seq)

    alignment_position = ma.get_real_position(encoded_alignment,
                                              mutation_site_0, 0)
    predicted_phosph_wild = run_netphos(wild_seq_filename)
    predicted_phosph_mutant = run_netphos(mutant_seq_file.name)
    alignment = ma.preprocess_features(encoded_alignment)

    os.remove(mutant_seq_file.name)

    surrounding_data = ma.analyze_predictions(predicted_phosph_wild,
                                              predicted_phosph_mutant,
                                              alignment, mutation_site_0,
                                              encoded_alignment)
    ptm_data = ma.analyze_ptms(alignment, mutation_site_0, alignment_position,
                               new_aa, predicted_phosph_mutant)
    motif_data = ma.analyze_motifs(alignment, proc_alignment, encoded_alignment,
                                   wild_seq, mutant_seq, mutation_site_0,
                                   alignment_position, feature_codemap,
                                   annotated_motifs)
    output = ma.combine_results(ptm_data, motif_data, surrounding_data,
                                disorder_prediction, mutation_site_0, wild_seq)
    # output = {
    #     'residues': [
    #         {
    #             'position': 1,  # 1-based!
    #             'disordered': 'Y',  # Y = Yes, N = No, M = Maybe
    #             'ptm': [{
    #                 'phosrel': ['certain/putative', 'N', 'description'],
    #                 'glycosylation': ['certain/putative', 'N', 'description']
    #             }],
    #             'motifs': [{
    #                 'motif-a': ['certain/putative', 'M', 'description'],
    #                 'motif-b': ['certain/putative', 'M', 'description']
    #             }],
    #         }
    #     ]
    # }
    return output


@celery_app.task
def update_elmdb(output_filename):
    _log.info("Running elm update")
    elm_url = "http://elm.eu.org/elms/browse_elms.tsv"
    go_url = "http://geneontology.org/ontology/go-basic.obo"
    elm_list = elm.get_data_from_url(elm_url)
    go_terms_list = elm.get_data_from_url(go_url)
    outtext = ""
    go_families = dict()
    for i in elm_list[6:]:
        lineI = re.split('\t|"', i)
        elm_id = lineI[4]
        pattern = lineI[10]
        prob = lineI[13]
        motif_go_terms = elm.get_motif_go_terms(elm_id)
        go_terms_extended = elm.extend_go_terms(go_terms_list, motif_go_terms,
                                                go_families)
        outtext += "{} {} {} {}\n".format(elm_id, pattern,
                                          prob, ' '.join(go_terms_extended))
    out = open(output_filename, 'w')
    out.write(outtext)
    _log.debug("Finished updating elm")
    out.close()


def get_task(output_type):
    """
    Get the task for the given output_type.

    If the output_type is not allowed, a ValueError is raised.
    """
    _log.info("Getting task for output '{}'".format(output_type))
    if output_type in ['predict', 'predict_and_align', 'align', 'refine',
                       'annotate']:
        task = postprocess
    elif output_type == 'hope':
        task = analyze_mutation
    else:
        raise ValueError("Unexpected output_type '{}'".format(output_type))

    _log.debug("Got task '{}'".format(task.__name__))
    return task
