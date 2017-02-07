#!/bin/bash

cd /data
/usr/bin/wget -N ftp://ftp.ncbi.nlm.nih.gov/blast/db/nr.\*.tar.gz
for ar in nr.*.tar.gz; do
    /bin/tar --overwrite -xzf $ar
done

if ! [ -d blast ] ; then mkdir blast; fi
cd blast
/usr/bin/wget -N ftp://ftp.ebi.ac.uk/pub/databases/uniprot/current_release/knowledgebase/complete/uniprot_sprot.fasta.gz
/bin/gunzip uniprot_sprot.fasta.gz
/usr/bin/makeblastdb -in uniprot_sprot.fasta -out sprot -dbtype prot -parse_seqids
