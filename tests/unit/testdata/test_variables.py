

alignment_7c = ">1\nSAAAAAAEAAAAAAQAAAAAA-AAAAAA-AAAAAA-AAAAAA\n>2\nSAAAAAAEAAAAAAQAAAAAASAAAAAAEAAAAAAQAAAAAA\n"
alignment_7c_list = [['1', 'SAAAAAAEAAAAAAQAAAAAA-AAAAAA-AAAAAA-AAAAAA'], ['2', 'SAAAAAAEAAAAAAQAAAAAASAAAAAAEAAAAAAQAAAAAA']]
alignment_1c = ">1\nSEQ---\n>2\nSEQSEQ\n"
alignment_1c_list = [['1', 'SEQ---'], ['2', 'SEQSEQ']]
d2p2_result = ['D2P2', [0, 0, 0]]
pred_result = [['predisorder', [0, 0, 0]],
               ['disopred', [0, 0, 0]],
               ['psipred', [0, 0, 0]],
               ['spine', [0, 0, 0]]]

processed_pred_result = [['predisorder', [0,0,0]],
                         ['disopred', [0, 0, 0]],
                         ['psipred', [0, 0, 0]],
                         ['spine', [0, 0, 0]],
                         ['consensus', [0, 0, 0]],
                         ['filtered', [0, 0, 0]]]

seq = 'SEQ'
fasta = '>1\nSEQ\n'
encoded_seq = '>1\nSAAAAAAEAAAAAAQAAAAAA\n## PROBABILITIES\nmotif index  probability\n'
ins_human_seq = ['>sp|P01308|INS_HUMAN Insulin OS=Homo sapiens GN=INS PE=1 SV=1\n', 'MALWMRLLPLLALLALWGPDPAAAFVNQHLCGSHLVEALYLVCGERGFFYTPKTRREAED'
                                                                                  +'LQVGQVELGGGPGAGSLQPLALEGSLQKRGIVEQCCTSICSLYQLENYCN']


