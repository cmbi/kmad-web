import json
import logging
import os
import subprocess
import re
import tempfile
import urllib2

from celery import current_app as celery_app

from kmad_web import paths

from kmad_web.helpers import txtproc

from kmad_web.services import files, iupred
from kmad_web.services import mutation_analysis as ma
from kmad_web.services.consensus import (find_consensus_disorder,
                                         filter_out_short_stretches)
from kmad_web.services.files import (get_fasta_from_blast,
                                     disopred_outfilename,
                                     predisorder_outfilename,
                                     psipred_outfilename)
from kmad_web.domain.blast.provider import BlastResultProvider
from kmad_web.domain.sequences.provider import UniprotSequenceProvider
from kmad_web.domain.sequences.annotator import SequenceAnnotator
from kmad_web.domain.sequences.encoder import SequenceEncoder
from kmad_web.domain.fles import write_fles, parse_fles
from kmad_web.domain.mutation import Mutation
from kmad_web.domain.updaters.elm import ElmUpdater
from kmad_web.default_settiings import KMAD


logging.basicConfig()
_log = logging.getLogger(__name__)


@celery_app.task
def postprocess(result, single_filename, multi_filename, conffilename,
                output_type):

    _log.info("Running postprocess")
    # process result and remove tmp files
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
        filtered_disorder = filter_out_short_stretches(consensus[1])
        result = result[:-1] + [consensus] + [result[-1]]
        # so that the alignment stays at the very end
        result = result[:-1] + [filtered_disorder, result[-1]]
        filtered_motifs_aln = txtproc.filter_motifs(result[-1]['alignments'][2],
                                                    filtered_disorder)
        result[-1]['alignments'].append(filtered_motifs_aln)
    elif (output_type == 'predict'
          and (len(result) > 2 and not result[1][0] == 'D2P2')):
        consensus = find_consensus_disorder(result[1:])
        result += [consensus]
        result += [filter_out_short_stretches(consensus[1])]
    elif output_type in ['predict_and_align', 'hope']:
        result = [result[0]] + result[-2:]
    elif output_type == 'predict':
        result = result[:2]
    return result


@celery_app.task
def run_single_predictor(prev_result, fasta_file, pred_name):
    _log.info("Run single predictor: {}".format(pred_name))
    # TODO: factor this IF statement out
    if prev_result[1][0]:
        return prev_result[1][1]
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
                data = subprocess.check_output(args)
            except (subprocess.CalledProcessError, OSError) as e:
                _log.error("Error: {}".format(e))
        elif pred_name == 'iupred':
            method = os.path.join(paths.IUPRED_DIR, 'iupred')
            args = [method, fasta_file, 'long']
            env = {"IUPred_PATH": paths.IUPRED_DIR}
            try:
                data = subprocess.check_output(args, env=env)
            except (subprocess.CalledProcessError, OSError) as e:
                _log.error("Error: {}".format(e))
        try:
            if pred_name not in ['globplot', 'iupred']:
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
                        "Output file {} doesn't exist".format(out_file))
            data = txtproc.preprocess(data, pred_name)
        except (subprocess.CalledProcessError, OSError) as e:
            _log.error("Error: {}".format(e))
    return data


@celery_app.task
def annotate(d2p2, filename):
    _log.info("Running annotate")

    convert_result = convert_to_7chars(filename)

    import subprocess
    subprocess.call(['cp', convert_result['filename'],
                     convert_result['filename'] + '2'])

    encoded_filename = convert_result['filename']
    with open(filename.split('.')[0] + '.map') as a:
        feature_codemap = a.read().splitlines()
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
    # TODO: Does this need to be a task?

    _log.info("Running get seq")
    result = txtproc.unwrap(fasta_file.splitlines())[1]
    return result


@celery_app.task
def run_blast(fasta_sequence):
    # out_blast = filename.split(".")[0]+".blastp"
    # args = ["blastp", "-query", filename, "-evalue", "1e-5",
    #         "-num_threads", "15", "-db", paths.SWISSPROT_DB,
    #         "-out", out_blast, '-outfmt', '10', '-max_target_seqs',
    #         str(seq_limit)]
    # try:
    #     subprocess.call(args)
    # except subprocess.CalledProcessError as e:
    #     _log.error("Error: {}".format(e.output))
    # with open(out_blast) as a:
    #     output = a.read().splitlines()
    # return output
    _log.info("Running blast")
    tmp_file = tempfile.NamedTemporaryFile(suffix=".fasta", delete=True)
    with tmp_file as f:
        f.write(fasta_sequence)

    blast = BlastResultProvider()
    blast_result = blast.get_result(tmp_file.name)
    return blast_result


@celery_app.task
def get_sequences_from_blast(blast_result):
    sequences = []
    uniprot = UniprotSequenceProvider()
    for s in blast_result:
        sequence = uniprot.get_sequence(s['id'])
        sequences.append(sequence)
    return sequences


@celery_app.task
def create_fles(sequences):
    """
    Create FLES file (input file for KMAD)

    :param sequences: list sequence dictionaries ({'header': '', 'seq': ''})
    :return: filename
    """
    annotator = SequenceAnnotator()
    annotator.annotate(sequences)
    encoder = SequenceEncoder()
    encoder.encode(sequences)
    return {
        'fles_path': write_fles(sequences),
        'sequences': sequences,
        'motif_code_dict': encoder.motif_code_dict,
        'domain_code_dict': encoder.domain_code_dict
    }


@celery_app.task
def run_kmad(create_fles_result, gop, gep, egp, ptm_score, domain_score,
             motif_score, conf_path=None, gapped=False, full_ungapped=False):
    """
    Run KMAD on the given fles_filename and return aligned sequences (dict)

    :fles_path: path to the FLES file (with encoded sequences)
    :gop: gap opening penalty
    :gep: gap extension penalty
    :egp: end gap penalty
    :ptm_score: feature weight for PTMs
    :motif_score: feature weight for motifs
    :domain_score: feature weight for domains
    :conf_path: path to the configuration file
    :gapped: True for standard alignment
    :full_ungapped: indel-free alignment but in a standard alignment format
                    (no residues are cut out from the final alignment,
                     but in all alignment rounds profile length is equal
                     query sequence length)
    """
    fles_path = create_fles_result['fles_path']
    sequences = create_fles_result['sequences']
    args = [KMAD, '-i', fles_path, '-o', fles_path, '-g', gop, '-e', gep,
            '-n', egp, '-p', ptm_score, '-m', motif_score, '-d', domain_score,
            '--out-encoded', '-c', '7']
    result_path = fles_path + '_al'
    # additional parameters
    if conf_path:
        args.extend(['--conf', conf_path])
    if gapped:
        args.extend(['--gapped'])
    elif full_ungapped:
        args.extend(['--full_ungapped'])

    try:
        subprocess.call(args)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(e)
    else:
        return {
            'fles_path': result_path,
            'sequences': sequences,
            'motif_code_dict': create_fles_result['motif_code_dict'],
            'domain_code_dict': create_fles_result['domain_code_dict']
        }


@celery_app.task
def process_kmad_alignment(run_kmad_result):
    fles_path = run_kmad_result['fles_path']
    sequences = run_kmad_result['sequences']

    alignment = parse_fles(fles_path)
    for s_index, s in enumerate(alignment):
        sequences[s_index]['aligned'] = s['seq']
    return {
        'sequences': sequences,
        'motif_code_dict': run_kmad_result['motif_code_dict'],
        'domain_code_dict': run_kmad_result['domain_code_dict']
    }


@celery_app.task
def analyze_mutation(process_kmad_result, fasta_sequence, position, mutant_aa,
                     feature_type):
    sequences = process_kmad_result['sequences']
    mutation = Mutation(sequences[0], position, mutant_aa)
    if feature_type == 'motifs':
        result = mutation.analyze_motifs(feature_type)
    elif feature_type == 'ptms':
        result = mutation.analyze_ptms(feature_type)
    else:
        raise RuntimeError("Unknown feature_type: {}".format(feature_type))
    return result


@celery_app.task
def query_d2p2(blast_result, filename, output_type, multi_seq_input):
    _log.info("Running query_d2p2")

    found_it = False
    prediction = []
    try:
        if not (multi_seq_input and output_type == 'align'):
            [found_it, seq_id] = txtproc.find_seqid_blast(blast_result)
            # seq_length -> temporary solution, until D2P2 fixes their bug
            #               (that sometimes predictions can be too short -
            #                than annotate missing residues as 'ambiguous
            #                disorder prediction'(code 5)
            seq_length = int(blast_result[0].split(',')[3])
            if found_it:
                data = 'seqids=["%s"]' % seq_id
                request = urllib2.Request('http://d2p2.pro/api/seqid', data)
                response = json.loads(urllib2.urlopen(request).read())
                if response[seq_id]:
                    pred_result = \
                        response[seq_id][0][2]['disorder']['consensus']
                    '''
                    if len(pred_result) < seq_length:
                        pred_result.extend([5 for i in range(len(pred_result),
                                                             seq_length + 1)])
                    elif len(pred_result) > seq_length:
                        pred_result = pred_result[:seq_length]
                    '''
                    if len(pred_result) == seq_length:
                        prediction = txtproc.process_d2p2(pred_result)
                    else:
                        found_it = False
                else:
                    found_it = False
    except urllib2.HTTPError and urllib2.URLError:
        _log.debug("D2P2 HTTP/URL Error")
    return [blast_result, [found_it, prediction]]


# @celery_app.task
# def analyze_mutation(processed_result, mutation_site, new_aa,
#                      wild_seq_filename):
#     _log.info("Running analyse mutation")
#
#     mutation_site_0 = mutation_site - 1  # 0-based mutation site position
#     wild_seq = processed_result[0]
#
#     disorder_prediction = processed_result[-2]  # filtered consensus
#     encoded_alignment = processed_result[-1]['alignments'][2]
#     proc_alignment = processed_result[-1]['alignments'][1]
#     feature_codemap = processed_result[-1]['alignments'][3]
#
#     annotated_motifs = processed_result[-1]['annotated_motifs']
#
#     mutant_seq = ma.create_mutant_sequence(wild_seq, mutation_site_0, new_aa)
#     mutant_seq_file = tempfile.NamedTemporaryFile(suffix=".fasta", delete=False)
#     with mutant_seq_file as f:
#         f.write('>mutant\n{}\n'.format(mutant_seq))
#
#     alignment_position = ma.get_real_position(encoded_alignment,
#                                               mutation_site_0, 0)
#     predicted_phosph_wild = run_netphos(wild_seq_filename)
#     predicted_phosph_mutant = run_netphos(mutant_seq_file.name)
#     alignment = ma.preprocess_features(encoded_alignment)
#
#     os.remove(mutant_seq_file.name)
#
#     surrounding_data = ma.analyze_predictions(predicted_phosph_wild,
#                                               predicted_phosph_mutant,
#                                               alignment, mutation_site_0,
#                                               encoded_alignment)
#     ptm_data = ma.analyze_ptms(alignment, mutation_site_0, alignment_position,
#                                new_aa, predicted_phosph_mutant)
#     motif_data = ma.analyze_motifs(alignment, proc_alignment, encoded_alignment,
#                                    wild_seq, mutant_seq, mutation_site_0,
#                                    alignment_position, feature_codemap,
#                                    annotated_motifs)
#     output = ma.combine_results(ptm_data, motif_data, surrounding_data,
#                                 disorder_prediction, mutation_site_0, wild_seq)
#     # output = {
#     #     'residues': [
#     #         {
#     #             'position': 1,  # 1-based!
#     #             'disordered': 'Y',  # Y = Yes, N = No, M = Maybe
#     #             'ptm': [{
#     #                 'phosrel': ['Y', 'N', 'description'],
#     #                 'glycosylation': ['M', 'N', 'description']
#     #             }],
#     #             'motifs': [{
#     #                 'motif-a': ['Y', 'M', 'description'],
#     #                 'motif-b': ['Y', 'M', 'description']
#     #             }],
#     #         }
#     #     ]
#     # }
#     return output


@celery_app.task
def update_elmdb(output_filename):
    elm = ElmUpdater()
    elm.update()


@celery_app.task
def filter_blast(blast_result):
    _log.debug('Filtering blast result')

    with open(paths.MAMMAL_IDS) as a:
        mammal_ids = a.read().splitlines()

    first_id = blast_result[0].split('|')[4].split('_')[1].split(',')[0]
    if first_id in mammal_ids:
        filtered_blast = []
        for i in blast_result:
            if i.split('|')[4].split('_')[1].split(',')[0] in mammal_ids:
                filtered_blast.append(i)
    else:
        filtered_blast = blast_result
    _log.info('Filtered blast: {}'.format(filtered_blast))
    return filtered_blast


@celery_app.task
def stupid_task(prev_result):
    return prev_result


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
