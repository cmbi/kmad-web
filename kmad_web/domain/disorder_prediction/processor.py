import logging


_log = logging.getLogger(__name__)


class PredictionProcessor(object):
    def process_prediction(self, prediction, pred_name):
        # 0 - structured, 2 - disordered
        _log.debug("{} returned: {}".format(pred_name, prediction))
        if pred_name == "spined":
            prediction_lines = prediction.splitlines()
            disorder_list = self._process_spined(prediction_lines)
        elif pred_name == "disopred":
            prediction_lines = prediction.splitlines()
            disorder_list = self._process_disopred(prediction_lines)
        elif pred_name == "psipred":
            prediction_lines = prediction.splitlines()
            disorder_list = self._process_psipred(prediction_lines)
        elif pred_name == "predisorder":
            prediction_lines = prediction.splitlines()
            disorder_list = self._process_predisorder(prediction_lines)
        elif pred_name == "globplot":
            prediction_lines = prediction.splitlines()
            disorder_list = self._process_globplot(prediction_lines)
        elif pred_name == "iupred":
            prediction_lines = prediction.splitlines()
            disorder_list = self._process_iupred(prediction_lines)
        elif pred_name == 'd2p2':
            disorder_list = self._process_d2p2(prediction)
        return disorder_list

    def get_consensus_disorder(self, predictions):
        consensus = []
        half = float(len(predictions.keys()))/2
        pred_keys = predictions.keys()
        for i in range(len(predictions[pred_keys[0]])):
            column = [predictions[k][i] for k in pred_keys]
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
                if (curr_length < 4 and curr_length < prev_length and
                        prev_state == next_state and
                        curr_length < self._find_next_length(disorder_list, i)):
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
        for i in prediction:
            if i >= 7:
                disorder_list += [2]
            elif i >= 5:
                disorder_list += [1]
            else:
                disorder_list += [0]
        return disorder_list

    def _process_spined(self, prediction_lines):
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
        _log.debug(prediction_lines)
        dis_regions = [i.split('-')
                       for i in prediction_lines[0].split(':')[-1].split(', ')]
        disorder_list = [0 for i in xrange(seqlength)]
        for i in dis_regions:
            if i[0] and i[1]:
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

    def make_text(self, predictions, sequence):
        pred_text = []
        if predictions:
            order = ['consensus', 'filtered', 'disopred', 'globplot', 'iupred',
                     'predisorder', 'psipred', 'globplot', 'spined', 'd2p2']
            # method names present in the predictions dict sorted by index in
            # the order list
            methods = sorted(predictions.keys(), key=lambda x: order.index(x))
            for k, v in predictions.iteritems():
                if len(v) != len(sequence):
                    _log.error("Prediction from {} has different length ({}) "
                               "than the seuence ({}).\nPrediction: {}\n"
                               "Sequence: {}\n".format(
                                   k, len(v), len(sequence), v, sequence))

            filtered = {k: v for k, v in predictions.iteritems() if
                        len(v) == len(sequence)}
            if len(predictions) != len(filtered):
                _log.warn("Not all predictions are of the same length as the "
                          "sequence")
                predictions = filtered
            pred_text.append("ResNo AA {}".format(
                ' '.join(methods)
            ))
            for j in xrange(len(sequence)):
                pred_text.append("{} {} {}".format(
                    str(j + 1), sequence[j],
                    ' '.join([str(predictions[m][j]) for m in methods])
                ))

        return '\n'.join(pred_text)
