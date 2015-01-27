import logging


logging.basicConfig()
_log = logging.getLogger(__name__)


def preprocess_spine(pred_out):
    disorder_list = []
    disorder_symbol = 'D'
    for i, lineI in enumerate(pred_out):
        line_list = lineI.split()
        if len(line_list) > 1:
            disorder = 0
            if line_list[1] == disorder_symbol:
                disorder = 2
            disorder_list += [disorder]
    return disorder_list


def preprocess_disopred_psipred(pred_out, pred_name):
    disorder_list = []
    if pred_name == "disopred":
        start = 3
        disorder_symbol = '*'
    else:
        start = 2
        disorder_symbol = 'C'
    for i, lineI in enumerate(pred_out[start:]):
        line_list = lineI.split()
        if len(line_list) > 2:
            if line_list[2] == disorder_symbol:
                disorder = 2
            else:
                disorder = 0
            disorder_list += [disorder]
    return disorder_list


def preprocess_predisorder(pred_out):
    disorder_list = []
    disorder_symbol = 'D'
    for i in range(len(pred_out[0].rstrip("\n"))):
        if pred_out[1][i] == disorder_symbol:
            disorder = 2
        else:
            disorder = 0
        disorder_list += [disorder]
    return disorder_list


def preprocess(pred_out, pred_name):
    pred_out_list = pred_out.split("\n")
    # 0 - structured, 2 - disordered
    if pred_name == "spine":
        disorder_list = preprocess_spine(pred_out_list)
    elif pred_name == "disopred" or pred_name == "psipred":
        disorder_list = preprocess_disopred_psipred(pred_out_list, pred_name)
    elif pred_name == "predisorder":
        disorder_list = preprocess_predisorder(pred_out_list)
    return [pred_name, disorder_list]


def process_fasta(fastafile):
    fasta_list = fastafile.splitlines()
    if fastafile.startswith('>'):
        sequence = ''.join(fasta_list[1:])
        new_fasta = fasta_list[0]+'\n'+sequence
    else:
        sequence = ''.join(fasta_list)
        new_fasta = '>fasta_header\n{}'.format(sequence)
    return new_fasta


def find_length(lines):
    length = 0
    for i in lines:
        if i.startswith('Length'):
            length = i.split('=')[1]
    return length


def find_seqid_blast(filename):
    with open(filename) as a:
        blast = a.read()
    blast = blast.splitlines()
    i = -1
    reading = True
    found = False
    seqID = ''
    while reading and i < len(blast):
        i += 1
        if "Query=" in blast[i]:
            query_length = find_length(blast[i+1:i+6])
        if "Sequences producing significant alignments" in blast[i]:
            i += 2
            e_val = blast[i].split()[-1]
            if e_val < '1e-5':
                j = i+1
                while j < len(blast):
                    if ">" in blast[j]:
                        linelist = blast[j+5].split()
                        hit_length = find_length(blast[j+1:j+6])
                        ''' check if identities equals 100% and gaps 0% and
                        length == query_length -> then it is the query sequence,
                        otherwise not found (this was the best hit)
                        '''
                        if (linelist[3] == "(100%)," and
                                linelist[-1] == "(0%)" and
                                query_length == hit_length):
                            found = True
                            seqID = blast[j].split("|")[1]
                        reading = False
                        break
                    else:
                        j += 1
            else:
                reading = False  # pragma: no cover
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
    processed = []
    processed_text = ""
    encoded = []
    for i in range(0, len(data_list), 2):
        header = data_list[i].split(' ')[0].lstrip('>')
        sequence = data_list[i+1][::codon_length]
        processed += [[header, sequence]]
        encoded += [[header, data_list[i+1]]]
        processed_text += "{}\n{}\n".format(data_list[i], sequence)
    return [processed_text, processed, encoded]


def decode(alignment, codon_length):
    data_list = alignment.splitlines()
    new_data_list = []
    for i in range(len(data_list)):
        if i % 2 == 0:
            new_data_list += [data_list[i]]
        else:
            new_data_list += [data_list[i][::codon_length]]
    return '\n'.join(new_data_list)
