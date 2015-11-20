from nose.tools import eq_

from kmad_web.parsers.netphos import NetphosParser


def test_parse():
    with open('tests/unit/testdata/netphos_result') as a:
        netphos_result = a.read()
    netphos_parser = NetphosParser()
    netphos_parser.parse(netphos_result)
    eq_(set([8, 34, 55]), netphos_parser.phosph_positions)
