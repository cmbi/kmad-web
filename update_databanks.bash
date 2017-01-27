cd /data
/usr/bin/wget ftp://ftp.ncbi.nlm.nih.gov/blast/db/FASTA/nr.gz
/bin/gunzip nr.gz
/usr/bin/makeblastdb -in nr -out nr -dbtype prot
