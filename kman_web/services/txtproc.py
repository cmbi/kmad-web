import logging


logging.basicConfig()
_log = logging.getLogger(__name__)


def preprocess(pred_out, pred_name):
    residue_list = []
    disorder_list = []
    pred_out_list = pred_out.split("\n")
    symbols = dict({"spine":"D","disopred":"*", "psipred":"C", "predisorder":"D"})
    disorder_symbol = symbols[pred_name]
    no = 0   ## disorder (0: structured, 1: maybe, 2: disordered)
    yes = 2
    if pred_name == "spine":
        for i, lineI in enumerate(pred_out_list):
            line_list = lineI.split()
            if len(line_list) > 1:	
                disorder = no 
                if line_list[1] == disorder_symbol:
                    disorder = yes
                residue_list += [line_list[0]]
                disorder_list += [disorder]
    elif pred_name == "disopred" or pred_name == "psipred":
        if pred_name =="disopred": start = 3
        else: start = 2
        for i, lineI in enumerate(pred_out_list[start:]):
            line_list = lineI.split()
            if len(line_list) > 2:	
                if line_list[2] == disorder_symbol:
                    disorder = yes
                else:
                    disorder = no
                residue_list += [line_list[1]]
                disorder_list += [disorder]
    elif pred_name == "predisorder":
        for i in range(len(pred_out_list[0].rstrip("\n"))):
            if pred_out_list[1][i] == disorder_symbol:
                disorder = yes
            else:
                disorder = no
            residue_list+=[pred_out_list[0][i]]
            disorder_list+=[disorder]
    residue_list = ''.join(residue_list)
    return [pred_name, disorder_list]


def process_fasta(fastafile):
    fasta_list = fastafile.splitlines()
    sequence = ''.join(fasta_list[1:])
    new_fasta = fasta_list[0]+"\n"+sequence
    return new_fasta


def lists_to_text(prediction):
    txt_pred = "# 0 - ordered; 2 - disordered; 1 - no consensus between methods (2:2)\n"
    header = ["ResNo","AA"]
    header += [i[0] for i in prediction[1:]]   #ResNo AA pred_name1 pred_name2 ....
    txt_pred += ' '.join(header)+"\n"
    for i in range(len(prediction[0])):
        newline = [i+1, prediction[0][i]]
        for j in range(1,len(prediction)):
            newline += [prediction[j][1][i]]
        newline += ["\n"]
        newline = [str(j) for j in newline]
        txt_pred += ' '.join(newline)
    return txt_pred


def find_seqid_blast(filename):
    blast = open(filename).readlines()
    i = -1 
    reading = True
    found = False
    seqID = ""
    while reading and i < len(blast):
        i += 1
        if "Query=" in blast[i]:
            query_length = blast[i+3].split("=")[1]
        if "Sequences producing significant alignments" in blast[i]:
            i += 2
            e_val = blast[i].split()[-1]
            seq_id = blast[i].split()[0].split("|")
            if e_val < '1e-5':
                j = i+1
                while j < len(blast):
                    if ">" in blast[j]:
                       linelist = blast[j+5].split()
                       hit_length = blast[j+2].split("=")[1]
                       #check if identities equals 100% and gaps 0% and length == query_length -> then it is the query sequence, otherwise not found (this was the best hit)
                       if linelist[3] == "(100%)," and linelist[-1] == "(0%)" and query_length == hit_length:   
                            found = True
                            seqID = blast[j].split("|")[1]
                       reading = False
                       break
                    else:
                       j += 1 
            else:
                reading = False
    return [found, seqID]


def process_d2p2(prediction):
    processed = []
    for i in prediction:
        if i >= 7:
            processed += [2]
        elif i >= 5:
            processed += [1]
        else:
            processed += [0]
    return ["D2P2", processed]
            
    
    

def process_alignment(data, codon_length):
     data_list = data.splitlines()
     return [[data_list[i].split(" ")[0].lstrip(">"),data_list[i+1][::codon_length]] for i in range(0,len(data_list),2)]


def decode(alignment, codon_length):
    data_list = alignment.splitlines()
    new_data_list = []
    for i in range(len(data_list)):
        if i % 2 == 0:
            new_data_list += [data_list[i]]
        else:
            new_data_list += [data_list[i][::codon_length]]
    return '\n'.join(new_data_list)

            
            
