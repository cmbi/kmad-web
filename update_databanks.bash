cd /data
/usr/bin/wget ftp://ftp.ncbi.nlm.nih.gov/blast/db/FASTA/nr.gz
/bin/gunzip nr.gz
/usr/bin/makeblastdb -in nr -out nr -dbtype prot -parse_seqids

if ! [ -d blast ] ; then mkdir blast; fi
cd blast
/usr/bin/wget ftp://ftp.ebi.ac.uk/pub/databases/uniprot/current_release/knowledgebase/complete/uniprot_sprot.fasta.gz
/bin/gunzip uniprot_sprot.fasta.gz
/usr/bin/makeblastdb -in uniprot_sprot.fasta -out sprot -dbtype prot -parse_seqids
