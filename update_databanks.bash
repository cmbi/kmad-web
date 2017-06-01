#!/bin/bash

cd /data
/usr/bin/wget -N ftp://ftp.ncbi.nlm.nih.gov/blast/db/nr.\*.tar.gz
for ar in nr.*.tar.gz; do
    name=${ar%.tar.gz}
    if [ $ar -nt $name'.psq' ] ; then
        /bin/tar --overwrite -xzf $ar
    fi
done

if ! [ -d blast ] ; then mkdir blast; fi
cd blast
/usr/bin/wget -N ftp://ftp.ebi.ac.uk/pub/databases/uniprot/current_release/knowledgebase/complete/uniprot_sprot.fasta.gz
/bin/gunzip -f uniprot_sprot.fasta.gz
/usr/bin/makeblastdb -in uniprot_sprot.fasta -out sprot -dbtype prot -parse_seqids

cd /data
if ! [ -d uniref ] ; then mkdir uniref; fi
cd uniref
/usr/bin/wget -N ftp://ftp.uniprot.org/pub/databases/uniprot/uniref/uniref90/uniref90.fasta.gz
if [ uniref90.fasta.gz -nt uniref90.pal ] ; then
    /bin/gunzip -f uniref90.fasta.gz
    /usr/local/bin/pfilt uniref90.fasta > uniref90filt.fasta
    /usr/local/bin/formatdb -i uniref90filt.fasta -t uniref90filt
    mv uniref90filt.fasta.pal uniref90filt.pal
    /usr/local/bin/formatdb -i uniref90.fasta -t uniref90
    mv uniref90.fasta.pal uniref90.pal
fi

cd /
/usr/bin/wget -N http://download.igb.uci.edu/sspro4.tar.gz
/bin/tar --overwrite -xzf sspro4.tar.gz sspro4/data/big --strip-components=1
