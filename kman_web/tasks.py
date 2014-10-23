import glob
import json
import logging
import os
import subprocess
import urllib2

from celery import current_app as celery_app, chord
from kman_web.default_settings import *

from kman_web.services.txtproc import preprocess, process_alignment, decode, find_seqid_blast, process_d2p2
from kman_web.services.consensus import find_consensus_disorder, filter_out_short_stretches
from kman_web.services.convert import convert_to_7chars
from kman_web.services.files import get_fasta_from_blast, disopred_outfilename, predisorder_outfilename, psipred_outfilename


logging.basicConfig()
_log = logging.getLogger(__name__)


@celery_app.task
def postprocess(result, filename, output_type):  
    ## process result and remove tmp files
    prefix = filename[0:14] 
    if glob.glob('%s*' % prefix):
        os.system('rm %s*' % prefix)    #rm /tmp/tmpXXXXXX*
    prefix = prefix[5:]
    if glob.glob('%s*' % prefix):
        os.system('rm %s*' % prefix)    #rm tmpXXXXXX*

    ## If the results are not form the d2p2 database, then process them (find consensus, and filter out short stretches)
    if output_type == 'predict_and_align' and not (len(result) == 3 and result[1][0] == 'D2P2'):
        consensus = find_consensus_disorder(result[1:-1])   ## first element is the sequence, last element is the alignement
        result = result[:-1] + [consensus] + [result[-1]]
        result = result[:-1] + [filter_out_short_stretches(consensus[1])] + [result[-1]]   ##so that the alignment stays at teh very end
    elif output_type == 'predict' and not (len(result) == 2 and result[1][0] == 'D2P2'):
        consensus = find_consensus_disorder(result[1:])
        result += [consensus]
        result += [filter_out_short_stretches(consensus[1])]
    return result


@celery_app.task
def run_single_predictor(d2p2_result, fasta_file, pred_name):
    out_dir = "kman_web/results"
    _log.debug("Run single predictor")
    if d2p2_result[0]:
        return d2p2_result[1]
    else:
        try:
            if pred_name == "dummy":
                sequence = open(fasta_file).readlines()[1:]
                sequence = [i.rstrip("\n") for i in sequence]
                sequence = ''.join(sequence)
                data = ["dummy", [0 for i in sequence]] 
            else:
                if pred_name == "spine":
                    tmp_name = fasta_file.split('/')[-1].split('.')[0]
                    tmp_path = '/'.join(fasta_file.split("/")[:-1])
                    method = SPINE_DIR+"/bin/run_spine-d"
                    args = [method, tmp_path, tmp_name]
                    out_file = SPINE_OUTPUT_DIR+tmp_name+".spd"
                    #out_file = "test.spd"
                elif pred_name == "disopred":
                    method = DISOPRED_PATH            
                    args = [DISOPRED_PATH, fasta_file]
                    out_file = disopred_outfilename(fasta_file)
                    #out_file = "test.diso"
                elif pred_name == "predisorder":
                    method = PREDISORDER_PATH
                    out_file = predisorder_outfilename(fasta_file)
                    #out_file = "test.predisorder"
                    args = [method, fasta_file, out_file]
                elif pred_name == "psipred":
                    method = PSIPRED_PATH
                    out_file = psipred_outfilename(fasta_file)
                    #out_file = "test.ss2"
                    args = [method, fasta_file]
                _log.debug("Running command '{}'".format(args))
                output = subprocess.call(args)
                with open(out_file) as f:
                      data = f.read()
                data = preprocess(data, pred_name)  
        except subprocess.CalledProcessError as e:
            _log.error("Error: {}".format(e.output))
            raise RuntimeError(e.output)
        finally:
            return data

    
@celery_app.task
def align(d2p2, filename):
    try:
        out_blast = filename.split(".")[0]+".blastp"    ## blast result file already created in "query_d2p2"
        fastafile = get_fasta_from_blast(out_blast, filename)     ## fasta filename

        ## 7chars ##
        toalign = convert_to_7chars(fastafile)          ## .7c filename
        codon_length = 7
        ## end of 7 ##

        ## 1char ##
        #codon_length = 1
        #toalign = fastafile
        ## end of one ##

        al_outfile = "%s_al" % toalign
        args = ["KMAN","-i",toalign,"-o",toalign,"-g","-5","-e","-1","-c",str(codon_length)]
        output = subprocess.call(args)
        
        alignment = open(al_outfile).read().encode('ascii', errors='ignore')
    except subprocess.CalledProcessError as e:
        _log.error("Error: {}".format(e.output))
        raise RuntimeError(e.output)
    alignment_list = process_alignment(alignment, codon_length)
    alignment = decode(alignment, codon_length)
    return [alignment,alignment_list]


@celery_app.task
def get_seq(d2p2, fasta_file):
    return fasta_file.splitlines()[1].encode('ascii', errors='ignore')
    

@celery_app.task
def query_d2p2(filename):
    found_it = False
    prediction = []
    try:
        out_blast = filename.split(".")[0]+".blastp"
        args = ["blastp","-query",filename,"-evalue","1e-5","-num_threads","15","-db",SWISSPROT_DB,"-out",out_blast]
        output = subprocess.call(args)
        [found_it, seq_id] = find_seqid_blast(out_blast)
        if found_it:
            data = 'seqids=["%s"]' % seq_id
            request = urllib2.Request('http://d2p2.pro/api/seqid', data)
            response = json.loads(urllib2.urlopen(request).read())
            if response[seq_id]:
                prediction = process_d2p2(response[seq_id][0][2]['disorder']['consensus'])
            else:
                found_it = False
    except subprocess.CalledProcessError as e:
        _log.error("Error: {}".format(e.output))
        raise RuntimeError(e.output)
    return [found_it, prediction]

        
def get_task(output_type):
    """
    Get the task for the given output_type.

    If the output_type is not allowed, a ValueError is raised.
    """
    _log.info("Getting task for output '{}'".format(output_type))
    if output_type == 'predict' or output_type == "predict_and_align":
        task = postprocess
    else:
        raise ValueError("Unexpected output_type '{}'".format(output_type))

    _log.debug("Got task '{}'".format(task.__name__))
    return task

