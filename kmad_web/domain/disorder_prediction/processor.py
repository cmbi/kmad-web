

class PredictionProcessor(object):
    def _init_(self):
        pass

    def process_prediction(self, prediction_lines, pred_name):
        prediction_lines = prediction_lines.splitlines()
        # 0 - structured, 2 - disordered
        if pred_name == "spine":
            disorder_list = self._process_spine(prediction_lines)
        elif pred_name == "disopred":
            disorder_list = self._process_disopred(prediction_lines)
        elif pred_name == "psipred":
            disorder_list = self._process_disopred_psipred(prediction_lines)
        elif pred_name == "predisorder":
            disorder_list = self._process_predisorder(prediction_lines)
        elif pred_name == "globplot":
            disorder_list = self._process_globplot(prediction_lines)
        elif pred_name == "iupred":
            disorder_list = self._process_iupred(prediction_lines)
        elif pred_name == 'd2p2':
            disorder_list = self._process_d2p2(prediction_lines)
        return disorder_list

    def get_consensus_disorder(self, predictions):
        consensus = []
        half = float(len(predictions))/2
        for i in range(len(predictions[0])):
            column = [predictions[j][i] for j in range(len(predictions))]
            if column.count(0) > half:
                consensus += [0]
            elif column.count(2) > half:
                consensus += [2]
            else:
                consensus += [1]
        return consensus

    def _find_next_length(self, disorder_list, pos):
        state = disorder_list[pos]
        n_length = 1
        for i in disorder_list[pos+1:]:
            if i == state:
                n_length += 1
            else:
                break
        return n_length

    def filter_out_short_stretches(self, disorder_list):
        new_cons = []
        prev_length, curr_length = 0, 0
        # current state {no, maybe, yes} {0,1,2}
        prev_state, curr_state = disorder_list, disorder_list
        for i in range(len(disorder_list)):
            if disorder_list[i] == curr_state:
                curr_length += 1
            else:
                # the end of the current state - check if it's long enough
                # if not change it to another state & add the elements form
                # the curr_state to the new_cons
                next_state = disorder_list[i]
                if (curr_length < 4
                        and curr_length < prev_length
                        and prev_state == next_state
                        and curr_length < self._find_next_length(disorder_list,
                                                                 i)):
                    # add curr_length elements of previous(=next) state
                    new_cons += [prev_state for j in range(curr_length)]
                else:
                    new_cons += [curr_state for j in range(curr_length)]
                prev_length = curr_length
                prev_state = curr_state
                curr_state = disorder_list[i]
                curr_length = 1
        if curr_length < 4 and curr_length < prev_length:
            new_cons += [prev_state for j in range(curr_length)]
        else:
            new_cons += [curr_state for j in range(curr_length)]
        return new_cons

    def _process_d2p2(self, prediction):
        disorder_list = []
        for i in disorder_list:
            if i >= 7:
                disorder_list += [2]
            elif i >= 5:
                disorder_list += [1]
            else:
                disorder_list += [0]
        return disorder_list

    def _process_spine(self, prediction_lines):
        disorder_list = []
        disorder_symbol = 'D'
        for i, lineI in enumerate(prediction_lines):
            line_list = lineI.split()
            if len(line_list) > 1:
                disorder = 0
                if line_list[1] == disorder_symbol:
                    disorder = 2
                disorder_list += [disorder]
        return disorder_list

    def _process_disopred(self, prediction_lines):
        disorder_list = []
        start = 3
        disorder_symbol = '*'
        for i, lineI in enumerate(prediction_lines[start:]):
            line_list = lineI.split()
            if len(line_list) > 2:
                if line_list[2] == disorder_symbol:
                    disorder = 2
                else:
                    disorder = 0
                disorder_list += [disorder]
        return disorder_list

    def _process_psipred(self, prediction_lines):
        disorder_list = []
        start = 2
        disorder_symbol = 'C'
        for i, lineI in enumerate(prediction_lines[start:]):
            line_list = lineI.split()
            if len(line_list) > 2:
                if line_list[2] == disorder_symbol:
                    disorder = 2
                else:
                    disorder = 0
                disorder_list += [disorder]
        return disorder_list

    def _process_predisorder(self, prediction_lines):
        disorder_list = []
        disorder_symbol = 'D'
        for i in range(len(prediction_lines[0].rstrip("\n"))):
            if prediction_lines[1][i] == disorder_symbol:
                disorder = 2
            else:
                disorder = 0
            disorder_list += [disorder]
        return disorder_list

    def _process_globplot(self, prediction_lines):
        seqlength = len(''.join(prediction_lines[1:]))
        dis_regions = [i.split('-')
                       for i in prediction_lines[0].split(':')[-1].split(', ')]
        disorder_list = [0 for i in xrange(seqlength)]
        for i in dis_regions:
            start = int(i[0]) - 1
            end = int(i[1])
            for j in xrange(start, end):
                disorder_list[j] = 2
        return disorder_list

    def _process_iupred(self, prediction_lines):
        disorder_list = []
        for i in prediction_lines[9:]:
            dis_val = float(i.split()[-1])
            if dis_val >= 0.5:
                disorder_list.append(2)
            else:
                disorder_list.append(0)
        return disorder_list
