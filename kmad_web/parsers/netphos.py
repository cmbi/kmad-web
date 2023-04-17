import re


class NetphosParser(object):
    def __init__(self):
        self.phosph_positions = set()

    def parse(self, netphos_result):
        reg = re.compile("YES$")
        for line in netphos_result.splitlines():
            if list(reg.finditer(line)):
                self.phosph_positions.add(int(line.split()[2]))
