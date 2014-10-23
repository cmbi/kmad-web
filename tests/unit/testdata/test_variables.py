

alignment_7c = ">1\nSAAAAAAEAAAAAAQAAAAAA-AAAAAA-AAAAAA-AAAAAA\n>2\nSAAAAAAEAAAAAAQAAAAAASAAAAAAEAAAAAAQAAAAAA\n"
alignment_1c = ">1\nSEQ---\n>2\nSEQSEQ"
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
