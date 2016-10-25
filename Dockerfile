FROM ubuntu:16.04

RUN apt-get update
RUN apt-get install -y build-essential git wget gfortran

RUN mkdir -p /usr/src/app
RUN mkdir -p /deps

# kmad
RUN apt-get install -y libboost-all-dev libconfig++-dev
RUN git clone https://github.com/cmbi/kmad.git /deps/kmad ;\
    cd /deps/kmad ;\
    git checkout v1.08 ;\
    cd /deps/kmad ; ./configure ; make -j ; make install ;\
    rm -rf /deps/kmad

# Tisean
RUN wget -q http://www.mpipks-dresden.mpg.de/%7Etisean/TISEAN_3.0.1.tar.gz -P /deps ;\
    mkdir -p /deps/tisean ; tar zxf /deps/TISEAN_3.0.1.tar.gz -C /deps/tisean --strip-components=1 ;\
    cd /deps/tisean ; export FC=gfortran ;\
    ./configure ; make -j ; cp source_c/sav_gol /usr/local/bin ;\
    rm /deps/TISEAN_3.0.1.tar.gz ; rm -rf /deps/tisean

# GlobPipe
COPY globplot-fix_biopython.diff /usr/src/app
RUN wget -q http://globplot.embl.de/html/GlobPipe-2.3.tgz -P /deps;\
    mkdir -p /deps/globpipe ; tar zxf /deps/GlobPipe-2.3.tgz -C /deps/globpipe --strip-components=1 ;\
    patch /deps/globpipe/GlobPipe.py /usr/src/app/globplot-fix_biopython.diff ;\
    cp /deps/globpipe/GlobPipe.py /usr/local/bin ;\
    rm /deps/GlobPipe-2.3.tgz ; rm -rf /deps/globpipe

# netphos
# TODO: edit tsch script variables with sed
COPY vendor/netphos-3.1.Linux.tar.Z /deps
RUN mkdir -p /deps/netphos ; tar zxf /deps/netphos-3.1.Linux.tar.Z -C /deps/netphos --strip-components=1
RUN ln -s /deps/netphos/ape /usr/local/bin/netphos-3.1 ;\
    ln -s /usr/local/bin/netphos-3.1 netphos

# disopred
# TODO: edit run_disopred.pl after install
# TODO: delete downloaded archive and deps folder
# TODO: test
RUN wget -q http://bioinfadmin.cs.ucl.ac.uk/downloads/DISOPRED/OLD/DISOPRED3.15.tar.gz -P /deps;\
    mkdir -p /deps/disopred ; tar zxf /deps/DISOPRED3.15.tar.gz -C /deps/disopred --strip-components=1 ;\
    cd /deps/disopred/src ; make -j ; make install ;\
    rm /deps/DISOPRED3.15.tar.gz ; rm -rf /deps/disopred

# sspro4
# depends on volume mounts for nr, big
# depends on nciblast2.2.9
# TODO: **this is really huge. can we do something about it?** -> put in vendor with crap removed? data on cmbi4?
# TODO: edit process-blast.pl with sed (in readme)
# TODO: get libstdc++.so.5
# TODO: install?
COPY vendor/sspro4.tar.gz /deps
RUN mkdir -p /deps/sspro4 ; tar zxf /deps/sspro4.tar.gz -C /deps/sspro4 --strip-components=1 ;\
    cd /deps/sspro4 ;\
    mkdir -p /data/nr ; mkdir -p /data/big ;\
    sed -i '24s/.*/$install_dir = "\/deps\/sspro4";/' configure.pl ;\
    sed -i '44s/.*/$nr_db_dir = "\/data\/nr\/";/' configure.pl ;\
    sed -i '47s/.*/$big_db_dir = "\/data\/big\/";/' configure.pl ;\
    sed -i "s/$fileo.'.app'/$fileo/g" script/process-blast.pl ;\
    ./configure.pl

# predisorder
# TODO: follow readme instructions
# TODO: edit configure.pl using sed
# TODO: get libstdc++.so.5
# TODO: install?
RUN wget -q http://sysbio.rnet.missouri.edu/multicom_toolbox/tools/predisorder1.1.tar.gz -P /deps;\
    mkdir -p /deps/predisorder ; tar zxf /deps/predisorder1.1.tar.gz -C /deps/predisorder --strip-components=1

# TODO: follow instructions in readme
RUN wget -q http://bioinfadmin.cs.ucl.ac.uk/downloads/psipred/old_versions/psipred3.5.tar.gz -P /deps;\
    mkdir -p /deps/psipred3.5 ; tar zxf /deps/psipred3.5.tar.gz -C /deps/psipred3.5 --strip-components=1 ;\
    cd /deps/psipred3.5/src ; make -j ; make install ;\
    rm /deps/psipred3.5.tar.gz ; rm -rf /deps/psipred3.5

# psipred
# depends on nciblast2.2.9
# TODO: follow instructions in readme
# TODO: set paths in runpsipred
# TODO: delete downloaded archive and deps folder
# TODO: test
RUN wget -q http://bioinfadmin.cs.ucl.ac.uk/downloads/psipred/old_versions/psipred.4.0.tar.gz -P /deps;\
    mkdir -p /deps/psipred ; tar zxf /deps/psipred.4.0.tar.gz -C /deps/psipred --strip-components=1 ;\
    cd /deps/psipred/src ; make -j ; make install ;\
    rm /deps/psipred.4.0.tar.gz ; rm -rf /deps/psipred

# spine-x
# The sed command sets fortran, removing the prompt for a compiler.
# TODO: exports
RUN wget -q http://sparks-lab.org/pmwiki/download/lib/spineXpublic.tgz -P /deps;\
    mkdir -p /deps/spinex ; tar zxf /deps/spineXpublic.tgz -C /deps/spinex --strip-components=1
RUN cd /deps/spinex/code ;\
    sed -i '6s/read complr/complr=gfortran/' compile ;\
    ./compile

# iupred
# TODO: fix iupred.c?
# TODO: compile
# TODO: why not install in path?
# TODO: test
# TODO: delete downloaded archive and deps folder
COPY vendor/iupred.tar.gz /deps
RUN mkdir -p /deps/iupred ;\
    tar zxf /deps/iupred.tar.gz -C /deps/iupred --strip-components=1

# spine-d
# TODO: follow instructions in readme
# TODO: edit values in bin/run_spine-d
# TODO: test
RUN wget -q http://sparks-lab.org/pmwiki/download/lib/spinedlocal_v2.0.tar.gz -P /deps ;\
    mkdir -p /deps/spined ; tar zxf /deps/spinedlocal_v2.0.tar.gz -C /deps/spined --strip-components=1

# ncbi blast
RUN wget -q ftp://ftp.ncbi.nlm.nih.gov/blast/executables/legacy/2.2.9/blast-2.2.9-amd64-linux.tar.gz -P /deps ;\
    mkdir -p /deps/blast ;\
    tar zxf /deps/blast-2.2.9-amd64-linux.tar.gz -C /deps/blast --strip-components=1
