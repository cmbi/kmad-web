#!/bin/bash

cd /data
/usr/bin/wget -N ftp://ftp.ncbi.nlm.nih.gov/blast/db/nr.\*.tar.gz
for ar in nr.*.tar.gz; do
    /bin/tar --overwrite -xzf $ar
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
/bin/gunzip -f uniref90.fasta.gz
/usr/local/bin/pfilt uniref90.fasta > uniref90filt.fasta
/usr/bin/formatdb -i uniref90filt.fasta -t uniref90filt
mv uniref90filt.fasta.pal uniref90filt.pal
/usr/bin/formatdb -i uniref90.fasta -t uniref90
mv uniref90.fasta.pal uniref90.pal

cd /data
if ! [ -d big ] ; then mkdir big; fi
cd big
# TODO: /data/big/big_98_X database, required by Predisorder
