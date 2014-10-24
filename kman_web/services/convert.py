import logging
import math
import os
import re
import string
import tempfile
import urllib2

from itertools import cycle, islice
from operator import itemgetter

from kman_web.default_settings import *


logging.basicConfig()
_log = logging.getLogger(__name__)

def create_numbering():
    alphabet = list(string.ascii_lowercase) + list(string.ascii_uppercase) + [str(i) for i in range(0,10)]
    alphabet.remove("A")
    numbering  = []
    for i in alphabet:
    	for j in alphabet:
    		numbering += [i+j]
    return numbering

def readFASTA(fastafilename):
    with open(fastafilename) as a:
        fastafileList = a.readlines()
    result = []
    for i,elementI in enumerate(fastafileList):
        if ">" in elementI or ">" in fastafileList[i-1]:
            result += [elementI.rstrip("\n")]
        else:
            result[-1]+=elementI.rstrip("\n")
    return result


def processSlimsAllClasses(classes):
    result = dict()
    for i in classes[6:]:
        slim_id = re.sub('"','',i.split('"')[3])
        slim_probability = float(re.sub('"','',i.split('"')[9]))
        result[slim_id] = [slim_probability, i]
    return result


def getID(sequence):
    if len(sequence.split('|')) >= 3:
        return sequence.split('|')[2].split(' ')[0]
    else:
        return 'UNKNOWN_ID'


#    PFAM   #
def runPfamScan(filename):
    result =[]
    dom = []
    outname = '{}.pfam'.format(filename.split('.')[0])
    os.system("/home/joanna/bin/PfamScan/pfam_scan.pl -fasta {} -dir /home/joanna/data/Pfam | grep -v '#' > {}".format(filename, outname))

    with open(outname) as a:
        pfamscanResult = a.readlines()

    for i in pfamscanResult:
       if len(i.split())> 3 :
           result.append([int(i.split()[1]),int(i.split()[2])])
           dom.append(i.split()[5]+" "+i.split()[6])

    os.system('rm {}'.format(outname))

    return [result,dom]


#    NETPHOS   #
def runNetPhos(filename):
    phosphorylations = set([])
    outname = '{}.np'.format(filename.split('.')[0])
    os.system('netphos-3.1 {} > {}'.format(filename, outname))

    with open(outname) as a:
        netPhosOut = a.readlines()

    for lineI in netPhosOut:
        if len(lineI.split())>0 and lineI.split()[-1]=='YES':
            phosphorylations.add(int(lineI.split()[2]))

    os.system('rm {}'.format(outname))                             

    return list(phosphorylations)


def get_uniprot_txt(uniprot_id):
    with open(UNIPROT_DAT_DIR+uniprot_id+".dat") as a:
        uniprot_dat = a.read()
    uniprot_dat = uniprot_dat.splitlines()
    features = []
    for lineI in uniprot_dat:
        if lineI.startswith('FT'):
            features += [lineI]
    return features


#  UNIPROT  #
def findPhosphSites(uniprotID):
    phosphorylations = [[],[],[],[]] # [exp, by similarity, probable, potential] - and so it goes for the other ptms
    Nglycs = [[], [], [], []]
    Oglycs = [[], [], [], []]
    amids = [[], [], [], []]
    hydrox = [[], [], [], []]
    meth = [[], [], [], []]
    acetyl = [[], [], [], []]
    features = get_uniprot_txt(uniprotID)
    for i in features:
        ## first check status (exp, by sim, prb or potential)
        if "By similarity" in i:
            n = 1
        elif "Probable" in i:
            n = 2
        elif "Potential" in i:
            n = 3
        else:
            n = 0
        ## check ptm kind and insert site in the results list
        if ("Phospho" in i or "phosph" in i) and "MOD_RES" in i:
            phosphorylations[n].append(int(i.split()[3]))
        elif "MOD_RES" in i and "amide":
            amids[n].append(int(i.split()[3]))
        elif "Glycosylation" in i and "O-linked" in i:
            Oglycs[n].append(int(i.split()[3]))
        elif "Glycosylation" in i and "N-linked" in i:
            Nglycs[n].append(int(i.split()[3]))
        elif "MOD_RES" in i and "acetyl":
            acetyl[n].append(int(i.split()[3]))
        elif "MOD_RES" in i and "hydroxy" in i:
            hydrox[n].append(int(i.split()[3]))
        elif "MOD_RES" in i and "methyl" in i:
            meth[n].append(int(i.split()[3]))
    return [Oglycs,meth,hydrox,amids,Nglycs,acetyl,phosphorylations]


#filterOutOverlapping -> removes overlapping slims (the ones with lower probabilities are removed)
def filterOutOverlapping(lims, ids, probs):
    probs_with_indexes =[[i,probs[i]] for i in range(len(probs))]
    probs_with_indexes.sort(key=itemgetter(1))
    probs_with_indexes.reverse()
    new_lims = []
    new_ids = []
    new_probs = []
    for i in probs_with_indexes:
        goed = True
        start = lims[i[0]][0]
        end = lims[i[0]][1]
        for j in new_lims:
            if (start >= j[0] and start <= j[1]) or (end >= j[0] and end <= j[1]):
                goed = False
        if goed:
            new_lims.append(lims[i[0]])
            new_ids.append(ids[i[0]])
            new_probs.append(probs[i[0]])
    return new_lims, new_ids, new_probs


def searchELM(uniprotID, sequence, slims_all_classes):
    limits = []
    elms_ids = []
    probabilities = []
    req = urllib2.Request("http://elm.eu.org/start_search/"+uniprotID+".csv")
    response = urllib2.urlopen(req)
    features = response.read().splitlines()
    write = False
    for line in features:
        entry  = line.split()
        prob = 1
        if entry:
            if entry[3] == "False":
                prob = 1 + 1/math.log(slims_all_classes[entry[0]][0],10)
                if prob > 0:
                    limits.append([int(entry[1]),int(entry[2])])				
                    elms_ids.append(entry[0])
                    probabilities.append(prob)
    limits, elms_ids, probabilities = filterOutOverlapping(limits,elms_ids,probabilities)
    return [limits, elms_ids, probabilities]


def srepeat(string, n):
   return ''.join(islice(cycle(string), n))


## adds new domains/motifs to the dictionary, value is the encoded index (ab, ac, ...), key is the element's id
def addElementsToTheDictionary(newList, oldDict, dictkind):
    newDict=oldDict
    dIndexes=[]
    numbering = create_numbering()
    for i,elI in enumerate(newList):
        if len(elI) > 0:
            elID = elI.split('.')[0] if dictkind == "domains" else elI
            if elID not in newDict.keys():
                index = len(newDict.keys())
                encoded_index = numbering[index]
                newDict[elID] = encoded_index
    return newDict
## creates a list of codes for domains in myList
def get_codes(myDict, myList, mode):
    if mode == 'domains':
        result=[ myDict[i.split('.')[0]] for i in myList ]
    else:
        result=[ myDict[i] for i in myList ]
    return result


#code: "012345" 0 - aa; 1 - nothing yet; 2 - domain, 3 - phosph; 4,5 - motif
#argument 'results' -> list([domains,phosphorylations, methods, low complexity regions])
def sevenCharactersCode(results, myseq, domain_codes, slim_codes):
    code_table = [["Z","a","b","c"], #code table for PTMs
                  ["V","W","X","Y"],
                  ["R","S","T","U"],
                  ["J","K","L","M"],
                  ["F","G","H","I"],
                  ["B","C","D","E"],
                  ["N","O","P","Q"]] 
    newseq = ""
    #first encode sequence with no features
    for i in myseq: newseq+=i+"AAAAAA"
    #map results onto the sequence
    #domains
    newseq = list(newseq)
    for i,domI in enumerate(results[0]):
        start = domI[0]
        end = domI[1]
        domainsCode = domain_codes[i]
        j = 0 
        k = 0
        while j < end+1 and k < len(newseq):
            if k % 7 == 2 and j >= start:
                newseq[k] = domainsCode[0]
                newseq[k+1] = domainsCode[1]
            elif k % 7 == 0 and newseq[k] != "-":
                j += 1 
            k += 1
    # predicted phosphorylations
    if results[4]:
        k = 0
        l = 0
        end = max(results[4])    
        while k < end + 1 and l < len(newseq):
            if l % 7 == 4 and k in results[4]:
                newseq[l] = "d"
            if l % 7 == 0 and newseq[l] != "-":
                k += 1 
            l+=1
    # all annotated PTMs 
    print results[3]
    for i,ptmI in enumerate(results[3]):
        for j, ptmModeJ in enumerate(ptmI):
            if ptmModeJ:
                k = 0
                l = 0
                end = max(ptmModeJ)    
                while k < end + 1 and l < len(newseq):
                    if l % 7 == 4 and k in ptmModeJ:
                        newseq[l] = code_table[i][j]
                    if l % 7 == 0 and newseq[l] != "-":
                        k+=1 
                    l+=1
    ## SLiMs
    ## all the residue from start to end(including the residue on position 'end')  belong the the slim
    for i,slimI in enumerate(results[1]):
        if len(slimI) > 0:
            start = slimI[0] 
            end = slimI[1]
            slimsCode = slim_codes[i]
            k = 0 
            j = 0
            while j < end + 1 and k < len(newseq):
                if k % 7 == 5 and j >= start:
                    newseq[k] = slimsCode[0]
                    newseq[k+1] = slimsCode[1]
                elif k % 7 == 0 and newseq[k] != "-":
                    j+=1
                k+=1
    for i, lcrI in enumerate(results[2]):
        start  = lcrI[0]
        end = lcrI[1]
        lcr_code = "L"
        k = 0 
        j = 0
        while j < end +1 and k < len(newseq):
            if k % 7 == 1 and j >= start:
                newseq[k] = lcr_code
            elif k % 7 == 0 and newseq[k] != "-":
                j+=1
            k+=1
    return ''.join(newseq)


## creates a tmp fastafile and returns a path to it
def tmp_fasta(seq_id, seq):
    fasta_seq = ">{}\n{}\n".format(seq_id, seq)
    tmp_file = tempfile.NamedTemporaryFile(suffix=".fasta",delete=False)
    with tmp_file as f:
        f.write(fasta_seq)
    return tmp_file.name


def elm_db(filename):
    with open(filename) as a:
        slims_all_classes_pre = a.readlines()
    return processSlimsAllClasses(slims_all_classes_pre)
    
#MAIN
def convert_to_7chars(filename):
    slims_all_classes = elm_db(ELM_DB)
    seqFASTA = readFASTA(filename)
    outname = filename.split(".")[0]+".7c"
    domainsDictionary=dict()
    motifsDictionary = dict()
    motifProbsDict = dict()
    newfile = ""
    for i,seqI in enumerate(seqFASTA):
        if '>' not in seqI:
            seqI = seqI.rstrip("\n")
            seq_id = getID(seqFASTA[i-1]).rstrip('\n')
            header = seqFASTA[i-1].rstrip('\n')
            
            tmp_filename = tmp_fasta(seq_id, seqI)
            [pfam,domains] = runPfamScan(tmp_filename)
            predicted_phosph = runNetPhos(tmp_filename)

            os.system('rm {}'.format(tmp_filename))

            uniprot_results = findPhosphSites(seq_id)
            [elm,motifs_ids,probs] = searchELM(seq_id, seqI, slims_all_classes)  #elms - slims' coordinates, motifs - ids, probs - probabilities
            lc_regions = []

            domainsDictionary = addElementsToTheDictionary(domains,domainsDictionary,"domains") 
            motifsDictionary = addElementsToTheDictionary(motifs_ids,motifsDictionary, "slims") #motifs from all sequences are taken into account
            domains_codes = get_codes(domainsDictionary,domains,"domains")
            motifs_codes = get_codes(motifsDictionary,motifs_ids,"motifs")
            for i,indI in enumerate(motifs_codes):
                motifProbsDict[indI] = probs[i]

            resultsList = [pfam, elm, lc_regions, uniprot_results, predicted_phosph]
            newfile += '{}\n{}\n'.format(header,sevenCharactersCode(resultsList,seqI, domains_codes, motifs_codes))

    newfile += "## PROBABILITIES\n"
    newfile += "motif index  probability\n"
    for i in motifProbsDict:
        newfile += str(i)+" "+str(motifProbsDict[i])+"\n"

    out=open(outname,"w")
    out.write(newfile)
    out.close()

    return outname
    
