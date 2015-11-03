import re


class NetphosParser(object):
    def __init__(self):
        self.phosph_positions = set()

    def parse(self, netphos_result):
        for line in netphos_result.splitlines():
            reg = re.compile("YES")
            if list(reg.finditer(line)):
                self.phosph_positions.add(int(line.split()[2]))
