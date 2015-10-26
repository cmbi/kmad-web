from nose.tools import eq_

from kmad_web.services.go import GoService


def test_call():
    method = "getTermParents"
    go_term = "GO:0001940"
    go = GoService()
    go._url = "http://www.ebi.ac.uk/ontology-lookup/OntologyQuery.wsdl"
    result_parents = go.call(method, go_term, "GO")['item']
    eq_('GO:0045120', result_parents[0]['key'])

    method = "getTermChildren"
    go_term = "GO:0045120"
    distance = -1
    expected_keys = ['GO:0001940', 'GO:0001939']
    result_children = go.call(method, go_term, "GO", distance)['item']
    eq_([i['key'] for i in result_children], expected_keys)
