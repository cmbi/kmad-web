# TODO

* exported environment variables must be available when system restarts/users
  that runs programs that depend on them
* should I make a patch for the change in sspro?


# Tisean (done)

* wget http://www.mpipks-dresden.mpg.de/~tisean/TISEAN_3.0.1.tar.gz
* tar zxvf TISEAN_3.0.1.tar.gz
* cd Tisean_3.0.1
* export FC=gfortran
* ./configure
* make
* sudo cp source_c/sav_gol /usr/local/bin

# GlobPlot (done)
* install Tisean
* wget http://globplot.embl.de/html/GlobPipe-2.3.tgz
* tar zxvf GlobPipe-2.3.tgz
* cd GlobPipe-2.3
* patch GlobPipe.py globplot-fix_biopython.diff
* sudo cp GlobPipe.py /usr/local/bin
* test: GlobPipe.py 10 8 75 8 8 1crn.fasta

# netphos (done)

* get the netphos arhcive: http://www.cbs.dtu.dk/cgi-bin/nph-sw_request?netphos
        (sent by email)
* tar zxvf netphos-3.1.Linux.tar.Z
* follow installation instructions at
  http://www.cbs.dtu.dk/services/doc/netphos-3.1.readme
* netphos 1crn.fasta

# disopred (done & tested)

* wget http://bioinfadmin.cs.ucl.ac.uk/downloads/DISOPRED/DISOPRED3.15.tar.gz
* tar zxvf DISOPRED3.15.tar.gz /usr/local/src/disopred
* cd DISOPRED/src
* make
* sudo make install
* edit following paths in run_disopred.pl:
  * $NCBI_DIR = "/usr/bin/"
  * $SEQ_DB = "/data/uniref/uniref90"
* test: /usr/local/src/disopred/run_disopred.pl 1crn.fasta

# sspro4 (done & tested)

* depends on nr & blastpgp (ncbi blast 2.2.9)
* wget http://download.igb.uci.edu/sspro4.tar.gz
* tar zxvf sspro4.tar.gz
* mv sspro4 /usr/local/src/
* edit configure.pl
  * $install_dir = "/usr/local/src/sspro4/";
  * $nr_db_dir = "/data/nr/";
* sed -i "s/$fileo.'.app'/$fileo/g" /usr/local/src/sspro4/script/process-blast.pl
* get libstdc++.so.5 and append it to LD_LIBRARY_PATH
* ./configure.pl

# predisorder (done & tested)

* wget http://sysbio.rnet.missouri.edu/multicom_toolbox/tools/predisorder1.1.tar.gz
* tar zxvf predisorder1.1.tar.gz
* follow readme instructions, but use sspro4 instead of pspro2
* edit configure.pl
  * $install_dir = "/usr/local/src/predisorder/";
* get libstdc++.so.5
* test: cd ~ && /usr/local/src/predisorder/bin/predict_diso.sh ~/1crn.fasta jon


<!--# PSIPRED 3.5 (done & tested)-->

* this is only needed for the bin/pfilt binary which is needed to create a
        database for psipred 4.0
* wget http://bioinfadmin.cs.ucl.ac.uk/downloads/psipred/psipred3.5.tar.gz
* tar zxvf psipred3.5.tar.gz /usr/local/src/psipred
* follow installation instructions in readme:
  * cd src
  * make
  * sudo make install

# PSIPRED 4.0 (done & tested)

* depends on uniref90filt & blastpgp (ncbi blast 2.2.9)
* wget http://bioinfadmin.cs.ucl.ac.uk/downloads/psipred/psipred.4.0.tar.gz
* tar zxvf psipred.4.0.tar.gz /usr/local/src/psipred4.0
* follow installation instructions in readme:
  * cd src
  * make
  * sudo make install
  * set paths in runpsipred:
    * ncbidir = /usr/bin
    * dbname = /data/uniref/uniref90filt
    * execdir = /usr/local/src/psipred4.0/bin
    * datadir = /usr/local/src/psipred4.0/data
* test: /usr/local/src/psipred4.0/runpsipred 1crn.fasta


# SPINE-X (done)

* wget http://sparks-lab.org/pmwiki/download/lib/spineXpublic.tgz
* tar zxvf spineXpublic.tgz /usr/local/src/spinex
* cd code
* ./compile
* export spineXcodir=/usr/local/src/spinex/code
* export spineXblast=/usr

# IUPred (done)

* get iupred (sent by email): http://iupred.enzim.hu/Downloads.php
* >copy iupred.tar.gz to machine<
* tar zxvf iupred.tar.gz
* sudo mv iupred /usr/local/src
* cd /usr/local/src/iupred
* fix iupred.c (%zu format specifier)
* cc iupred.c -o iupred

# SPINE-D (done & tested)

* wget http://sparks-lab.org/pmwiki/download/lib/spinedlocal_v2.0.tar.gz
* tar zxvf spinedlocal_v2.0.tar.gz /usr/local/src/
* follow installation instructions in readme:
  * edit following values in bin/run_spine-d:
    * blastprog=/usr/local/blastpgp
    * nrdb=/data/nr/nr
    * spx=/usr/local/src/spinex
    * spd=/usr/local/src/spined
    * IUPred_PATH=/usr/local/src/iupred
* test: /usr/local/src/spined/bin/run_spine-d . 1crn

# uniref90filt

* depends on psipred 3.5 & ncbi blast 2.2.9 (for formatdb) (NOT blast+)
* wget ftp://ftp.uniprot.org/pub/databases/uniprot/uniref/uniref90/uniref90.fasta.gz
* gunzip uniref90.fasta.gz
* /usr/local/src/psipred/bin/pfilt uniref90.fasta > uniref90filt.fasta
* formatdb uniref90filt.fasta

# NCBI BLAST 2.2.9

* wget ftp://ftp.ncbi.nlm.nih.gov/blast/executables/legacy/2.2.9/blast-2.2.9-amd64-linux.tar.gz
* mkdir blast2.2.9 & cd blast2.2.9
* tar zxvf blast-2.2.9-amd64-linux.tar.gz

# nr db
* wget ftp://ftp.ncbi.nlm.nih.gov/blast/db/nr\*.tar.gz
* tar xzvf nr*.tar.gz
