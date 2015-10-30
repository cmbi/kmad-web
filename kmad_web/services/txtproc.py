import logging


logging.basicConfig()
_log = logging.getLogger(__name__)


def process_spine(pred_out):
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


def unwrap(seq_data):
    new = []
    for i in seq_data:
        if i.startswith('>'):
            new.append(i)
            new.append("")
        else:
            new[-1] += i
    return new


def process_disopred_psipred(pred_out, pred_name):
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


def process_predisorder(pred_out):
    disorder_list = []
    disorder_symbol = 'D'
    for i in range(len(pred_out[0].rstrip("\n"))):
        if pred_out[1][i] == disorder_symbol:
            disorder = 2
        else:
            disorder = 0
        disorder_list += [disorder]
    return disorder_list


def process_globplot(outlist):
    seqlength = len(''.join(outlist[1:]))
    dis_regions = [i.split('-') for i in outlist[0].split(':')[-1].split(', ')]
    disorder_list = [0 for i in xrange(seqlength)]
    for i in dis_regions:
        start = int(i[0]) - 1
        end = int(i[1])
        for j in xrange(start, end):
            disorder_list[j] = 2
    return disorder_list


def process_iupred(pred_out):
    disorder_list = []
    _log.info("first two: {}".format(pred_out[9:11]))
    for i in pred_out[9:]:
        dis_val = float(i.split()[-1])
        if dis_val >= 0.5:
            disorder_list.append(2)
        else:
            disorder_list.append(0)
    return disorder_list


def process_prediction(pred_out, pred_name):
    pred_out_list = pred_out.splitlines()
    # 0 - structured, 2 - disordered
    if pred_name == "spine":
        disorder_list = process_spine(pred_out_list)
    elif pred_name == "disopred" or pred_name == "psipred":
        disorder_list = process_disopred_psipred(pred_out_list, pred_name)
    elif pred_name == "predisorder":
        disorder_list = process_predisorder(pred_out_list)
    elif pred_name == "globplot":
        disorder_list = process_globplot(pred_out_list)
    elif pred_name == "iupred":
        disorder_list = process_iupred(pred_out_list)
    return disorder_list


def process_fasta(fastafile):
    fasta_list = unwrap(fastafile.splitlines())
    new_list = []
    if fastafile.startswith('>'):
        for i in fasta_list:
            if i.startswith('>'):
                new_list += [i + '\n']
            else:
                new_list[-1] += i
        new_fasta = '\n'.join(new_list)
    else:
        new_fasta = '>fasta_header\n{}'.format(''.join(fasta_list))
    return new_fasta


def find_length(lines):
    length = 0
    for i in lines:
        if i.startswith('Length'):
            length = i.split('=')[1]
    return length


def find_seqid_blast(blast_result):
    found = False
    seqID = ""
    if len(blast_result) > 0:
        firstline = blast_result[0].split(',')
        if (firstline[2] == "100.00"
                and firstline[4] == "0" and firstline[5] == "0"
                and firstline[10] == "0.0"
                and firstline[6:8] == firstline[8:10]):
            found = True
            seqID = firstline[1].split('|')[1]
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
    return processed


def process_alignment(data, codon_length):
    data_list = data.splitlines()
    if '## PROBABILITIES' in data_list:
        prob_index = data_list.index('## PROBABILITIES')
        data_list = data_list[:prob_index]
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


def check_if_multi(fasta_seq):
    count = 0
    reading = True
    i = 0
    fasta_list = fasta_seq.splitlines()
    while reading and i < len(fasta_list):
        if fasta_list[i].startswith('>'):
            count += 1
        if count > 1:
            reading = False
        i += 1
    if count > 1:
        return True
    else:
        return False


def parse_positions(pos):
    poslist = pos.replace(' ', '').split(',')
    parsed = []
    for i in poslist:
        if i.isdigit():
            parsed += [i]
        elif len(i.split('-')) == 2:
            parsed += [str(j) for j in xrange(int(i.split('-')[0]),
                                              int(i.split('-')[1]) + 1)]
    return parsed


def parse_features(usr_features):
    outtext = 'feature_settings = \n' \
              + '  {\n' \
              + '  usr_features = ( \n'
    feat_dict = {}
    for i in usr_features:
        i_positions = parse_positions(i['positions'])
        if i['featname'] not in feat_dict.keys():
            feat_dict[i['featname']] = {'name': i['featname'],
                                        'add_score': i['add_score'],
                                        'pattern': i['pattern'],
                                        'positions': [{'seq':
                                                       i['sequence_number'],
                                                       'pos':
                                                       i_positions
                                                       }]
                                        }
        else:
            feat_dict[i['featname']]['positions'] += [{'seq':
                                                       i['sequence_number'],
                                                       'pos': i_positions}]
    for i in feat_dict.keys():
        outtext += '{{    name = "{}";\n'.format(i) \
                   + '    tag = "";\n' \
                   + '    add_score = {};\n'.format(feat_dict[i]['add_score']) \
                   + '    subtract_score = "";\n' \
                   + '    add_features = ("{}");\n'.format(i) \
                   + '    add_tags = ();\n' \
                   + '    add_exceptions = ();\n' \
                   + '    subtract_features = ();\n' \
                   + '    subtract_tags = ();\n' \
                   + '    subtract_exceptions = ();\n' \
                   + '    pattern = "{}";\n'.format(feat_dict[i]['pattern']) \
                   + '    positions = ( '
        for j in feat_dict[i]['positions']:
            if j['seq']:
                outtext += '{{ seq = {}; pos = ({}); }}'.format(j['seq'],
                                                                ', '.join(j['pos']))
                if j != feat_dict[i]['positions'][-1]:
                    outtext += ','
            outtext += '\n'
        outtext += ');\n}\n'
    outtext += ');\n};\n'
    return outtext


def remove_empty(usr_features):
    new_features = usr_features[:]
    indexes = range(len(usr_features))
    indexes.reverse()
    for i in indexes:
        for j in usr_features[i].keys():
            if not usr_features[i][j]:
                del new_features[i]
                break
    return new_features


def filter_motifs(motif_aln, disorder):
    '''
    result = []
    if '0' in disorder:

    else:
        result = motif_aln[:]
    '''
    pass







