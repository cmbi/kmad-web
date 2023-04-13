import logging
import tempfile


_log = logging.getLogger(__name__)


class UserFeaturesParser(object):
    def _parse(self, user_features):
        outtext = 'feature_settings = \n' \
                  + '  {\n' \
                  + '  usr_features = ( \n'
        feat_dict = {}
        for i in user_features:
            i_positions = self._parse_positions(i['positions'])
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
                       + '    add_score = {};\n'.format(
                           feat_dict[i]['add_score']) \
                       + '    subtract_score = "";\n' \
                       + '    add_features = ("{}");\n'.format(i) \
                       + '    add_tags = ();\n' \
                       + '    add_exceptions = ();\n' \
                       + '    subtract_features = ();\n' \
                       + '    subtract_tags = ();\n' \
                       + '    subtract_exceptions = ();\n' \
                       + '    pattern = "{}";\n'.format(
                           feat_dict[i]['pattern']) \
                       + '    positions = ( '
            for j in feat_dict[i]['positions']:
                if j['seq']:
                    outtext += '{{ seq = {}; pos = ({}); }}'.format(
                        j['seq'], ', '.join(j['pos']))
                    if j != feat_dict[i]['positions'][-1]:
                        outtext += ','
                outtext += '\n'
            outtext += ');\n}\n'
        outtext += ');\n};\n'
        return outtext

    def write_conf_file(self, usr_features):
        usr_features = self._remove_empty(usr_features)
        if usr_features:
            parsed_features = self._parse(usr_features)
            tmp_file = tempfile.NamedTemporaryFile(suffix=".cfg", delete=False)
            _log.debug("Created tmp file '{}'".format(tmp_file.name))
            with tmp_file as f:
                _log.debug("Writing data to '{}'".format(tmp_file.name))
                f.write(parsed_features)
            return tmp_file.name
        else:
            return None

    def _remove_empty(self, usr_features):
        new_features = usr_features[:]
        indexes = list(range(len(usr_features)))[::-1]
        for i in indexes:
            for j in usr_features[i].keys():
                if not usr_features[i][j]:
                    # if pattern is empty but positions and seq number is not
                    #      then don't delete the feature (and if p and seq
                    #      number are empty but pattern is not
                    #      then also don't)
                    #
                    check1 = (j == 'pattern'
                              and not (usr_features[i]['positions']
                                       and usr_features[i]['sequence_number'])
                              )
                    check2 = ((j == 'positions' or j == 'sequence_number')
                              and not usr_features[i]['pattern']
                              )
                    check3 = (j != 'positions'
                              and j != 'pattern'
                              and j != 'sequence_number'
                              )
                    if check1 or check2 or check3:
                        del new_features[i]
                    break
        return new_features

    def _parse_positions(self, pos):
        poslist = pos.replace(' ', '').split(',')
        parsed = []
        for i in poslist:
            if i.isdigit():
                parsed += [i]
            elif len(i.split('-')) == 2:
                parsed += [str(j) for j in range(int(i.split('-')[0]),
                                                 int(i.split('-')[1]) + 1)]
        return parsed
