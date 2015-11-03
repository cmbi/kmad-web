

def decode(sequences):
    for s in sequences:
        s['seq'] = s['encoded_seq'][::7]
