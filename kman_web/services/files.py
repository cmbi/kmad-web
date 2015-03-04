import glob
import logging
import os
import tempfile
import time
import urllib2

from kman_web.services import txtproc


_log = logging.getLogger(__name__)


def is_empty(s1):
    if s1.isspace() or s1 == "":
        return True
    else:
        return False


def get_seq_from_uniprot(uniprot_id):
    req = urllib2.Request(
        "http://www.uniprot.org/uniprot/{}.fasta".format(uniprot_id))
    uniprot = urllib2.urlopen(req).readlines()
    for i, lineI in enumerate(uniprot):
        if lineI.startswith('>') and uniprot_id in lineI:
            header = lineI
            sequence = uniprot[i+1].rstrip("\n")
            j = i+2
            while j < len(uniprot) and ">" not in uniprot[j]:
                sequence += uniprot[j].rstrip("\n")
                j += 1
            break
    return [header, sequence]


def get_e_val(textline):
    e_val = textline.split()[-1]
    if e_val[0] == "e":
        e_val = "1"+e_val
    return float(e_val)


# gets fasta sequences from uniprot and writes them to file tmpXXX_toalign.fasta
# returns name of the file
# blast name - path to the file with blast results
# query_filename - path to the file with the original sequence
def get_fasta_from_blast(blast_name, query_filename):
    outfile_name = blast_name.split(".")[0]+"_toalign.fasta"
    outfile = open(outfile_name, 'w')
    with open(query_filename) as a:
        query_fasta = a.read()
    query_fasta = query_fasta.splitlines()
    with open(blast_name) as a:
        blastfile = a.read()
    blastfile = blastfile.splitlines()
    reading = False
    count = 0
    newfasta = ''
    i = -1
    while i < len(blastfile):
        i += 1
        lineI = blastfile[i]
        if "Sequences producing significant alignments" in lineI:
            reading = True
            i += 1
        elif reading and len(lineI.split()) > 0:
            e_val = get_e_val(lineI)
            if e_val <= 0.0001:
                uniprot_id = lineI.split(" ")[2].split("|")[2]
                sequence = get_seq_from_uniprot(uniprot_id)
                count += 1
                if count == 1 and sequence[1] != query_fasta[1]:
                        newfasta += query_fasta[0]+'\n'
                        newfasta += query_fasta[1]+'\n'
                elif count >= 35:   # pragma: no cover
                    _log.debug('Limit of sequences number reached')
                    break
                elif count % 10 == 0:     # pragma: no cover
                    time.sleep(5)
                if len(sequence[0]) > 1:
                    newfasta += sequence[0]
                    newfasta += sequence[1]+'\n'
        elif reading:
            break
    outfile.write(newfasta)
    outfile.close()
    return outfile_name


def disopred_outfilename(fasta_file):
    return '.'.join(fasta_file.split('.')[:-1])+".diso"


def psipred_outfilename(fasta_file):
    return ('.'.join(fasta_file.split('.')[:-1])+".ss2").split('/')[-1]


def predisorder_outfilename(fasta_file):
    return '.'.join(fasta_file.split('.')[:-1])+".predisorder"


def write_single_fasta(fasta_seq):
    fasta_list = fasta_seq.splitlines()
    newfile_list = [fasta_list[0]]
    reading = True
    i = 1
    while reading and i < len(fasta_list):
        if fasta_list[i].startswith('>'):
            reading = False
        else:
            newfile_list += [fasta_list[i]]
        i += 1
    tmp_file = tempfile.NamedTemporaryFile(suffix=".fasta", delete=False)
    _log.debug("Created tmp file '{}'".format(tmp_file.name))
    with tmp_file as f:
        _log.debug("Writing data to '{}'".format(tmp_file.name))
        f.write('\n'.join(newfile_list))
    return tmp_file.name


def remove_files(filename):
    prefix = filename[0:14]
    if glob.glob('%s*' % prefix):
        os.system('rm %s*' % prefix)    # pragma: no cover
    prefix = prefix[5:]
    if glob.glob('%s*' % prefix):
        os.system('rm %s*' % prefix)    # pragma: no cover


def write_conf_file(usr_features):
    parsed_features = txtproc.parse_features(usr_features)
    tmp_file = tempfile.NamedTemporaryFile(suffix=".cfg", delete=False)
    _log.debug("Created tmp file '{}'".format(tmp_file.name))
    with tmp_file as f:
        _log.debug("Writing data to '{}'".format(tmp_file.name))
        f.write(parsed_features)
    return tmp_file.name
