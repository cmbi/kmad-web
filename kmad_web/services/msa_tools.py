import os
import subprocess

from kmad_web import paths as p


def run_preliminary_alignment(fastafile, method):
    if method == "t_coffee":
        args = [os.path.join(p.KMAD_WEB_BIN, "t_coffee"), fastafile, "-output",
                "fasta_aln", "-outfile", fastafile + "_prel_al"]
    elif method == "muscle":
        args = [os.path.join(p.KMAD_WEB_BIN, "muscle"), "-in", fastafile,
                "-out", fastafile + '_prel_al']
    elif method == "clustalo":
        args = ["clustalo", "-i", fastafile, "-o", fastafile + '_prel_al']
    elif method == "mafft":
        args = [os.path.join(p.KMAD_WEB_BIN, "mafft"), fastafile]
    elif method == "clustalw":
        args = ["clustalw2", "-INFILE={}".format(fastafile),
                "-OUTFILE={}_prel_al".format(fastafile), "-OUTPUT=FASTA",
                "-OUTORDER=INPUT"]
    if method != 'mafft':
        subprocess.call(args)
    else:
        output = subprocess.check_output(args)
        out = open(fastafile + '_prel_al', 'w')
        out.write(''.join(output))
        out.close()
    return fastafile + '_prel_al'
