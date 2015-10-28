import tempfile

from kmad_web.default_settings import NETPHOS_PATH
from kmad_web.services.netphos import NetphosService
from kmad_web.parsers.netphos import NetphosParser


class NetphosFeatureProvider(object):
    def __init__(self):
        pass

    def get_phosphorylations(self, sequence):
        fasta_sequence = ">sequence\n{}\n".format(sequence)
        tmp_file = tempfile.NamedTemporaryFile(suffix=".fasta", delete=True)
        with tmp_file as f:
            f.write(fasta_sequence)
        netphos_service = NetphosService(NETPHOS_PATH)
        netphos_parser = NetphosParser()
        netphos_result = netphos_service.predict(tmp_file.name)
        netphos_parser.parse(netphos_result)
        phosphorylations = []
        for p in netphos_parser.phosph_positions:
            phosph = {'name': 'phosphorylation',
                      'annotation_level': 4,
                      'positions': p
                      }
            phosphorylations.append(phosph)
        return phosphorylations
