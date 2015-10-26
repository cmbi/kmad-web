from kmad_web.default_settings import NETPHOS_PATH
from kmad_web.services.netphos import NetphosService
from kmad_web.parsers.netphos import NetphosParser


class NetphosFeatureProvider(object):
    def __init__(self):
        self.phosphorylations = []

    def get_phosphorylations(self, fasta_filename):
        netphos_service = NetphosService(NETPHOS_PATH)
        netphos_parser = NetphosParser()

        netphos_result = netphos_service.predict(fasta_filename)
        netphos_parser.parse(netphos_result)
        for p in netphos_parser.phosph_positions:
            phosph = {'name': 'phosphorylation',
                      'annotation_level': 4,
                      'positions': p
                      }
            self.phosphorylations.append(phosph)
