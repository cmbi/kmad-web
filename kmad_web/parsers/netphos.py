import re


class NetphosParser(object):
    def __init__(self):
        self._phosph_postions = set()

    def parse(self, netphos_result):
        for line in netphos_result.splitlines():
            reg = re.compile("YES")
            if list(reg.finditer(line)):
                self._phosph_postions.add(int(line.split()[2]))
