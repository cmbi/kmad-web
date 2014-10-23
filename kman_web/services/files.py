from sys import argv
import logging
import subprocess
import time
import urllib
import urllib2

from kman_web.default_settings import *


_log = logging.getLogger(__name__)


def is_empty(s1):
    if s1.isspace() or s1 == "":
        return True
    else:
        return False


def get_calculated_results():
    output = subprocess.check_output(['ls', 'kman_web/frontend/static/results_html'])
    file_prefixes = set()
    for i in output.split("\n"):
        prefix = ".".join(i.split(".")[:-1])
        if not is_empty(prefix):
            file_prefixes.add(prefix)
    file_prefixes = list(file_prefixes)
    file_prefixes.sort()
    return file_prefixes


def get_seq_from_uniprot(uniprot_id):
    uniprot = open(UNIPROT_FASTA_DIR + uniprot_id + ".fasta").readlines()
    for i,lineI in enumerate(uniprot):
        if ">" == lineI[0] and uniprot_id in lineI:
            header = lineI
            sequence = uniprot[i+1].rstrip("\n")
            j = i+2
            while j < len(uniprot) and ">" not in uniprot[j]:
                sequence += uniprot[j].rstrip("\n")
                j += 1
            break
    return [header, sequence]


#gets fasta sequences from uniprot and writes them to file tmpXXX_toalign.fasta
#returns name of the file
def get_fasta_from_blast(blast_name, query_filename):
    outfile_name = blast_name.split(".")[0]+"_toalign.fasta"
    outfile = open(outfile_name,'w')
    query_fasta = open(query_filename).readlines()
    blastfile = open(blast_name).readlines()
    start_0 = False
    start_1 = False
    count = 0
    for i in blastfile:
        if "Sequences producing significant alignments" in i:
            start_0 = True
        elif start_0:
            start_1 = True
            start_0 = False
        elif start_1 and len(i.split()) > 0:
            e_val = i.split()[-1]
            if e_val[0] == "e":
                e_val = "1"+e_val
            e_val = float(e_val)
            if e_val <= 0.0001:
                uniprot_id = i.split(" ")[2].split("|")[2]
                sequence = get_seq_from_uniprot(uniprot_id)    
                count += 1
                if "\n" in sequence[1]:
                    _log.debug("There is a newline!")
                if count == 1:
                    if sequence[1] != query_fasta[1]:
                        _log.debug("first seq: "+sequence[1])
                        _log.debug("query_seq: "+query_fasta[1])
                        outfile.write(query_fasta[0]) 
                        outfile.write(query_fasta[1]+"\n") 
                if len(sequence[0]) > 1: 
                    outfile.write(sequence[0])
                    outfile.write(sequence[1]+"\n")
                if count % 10 == 0:
                    time.sleep(5)
        elif start_1:
            break
    outfile.close()
    return outfile_name
    

def disopred_outfilename(fasta_file):
    return '.'.join(fasta_file.split('.')[:-1])+".diso"


def psipred_outfilename(fasta_file):
    return ('.'.join(fasta_file.split('.')[:-1])+".ss2").split('/')[-1]


def predisorder_outfilename(fasta_file):
    return '.'.join(fasta_file.split('.')[:-1])+".predisorder" 







