from nose.tools import eq_, with_setup
import pprint as pp

from kmad_web.services.go import GoService
from kmad_web.services.helpers.cache import cache_manager as cm


def setup():
    cm.load_config({
        'redis': {'redis.backend': 'dogpile.cache.null'}
    })


def teardown():
    cm.reset()


@with_setup(setup, teardown)
def test_call():
    query_type = 'parents'
    go_term = "GO_0001940"
    go = GoService()
    go._url = "http://www.ebi.ac.uk/ols/api/ontologies/go/terms/http%253A%252F%252Fpurl.obolibrary.org%252Fobo%252F"
    result_parents = go.call(go_term, query_type)
    eq_('GO:0045120', result_parents[0]['obo_id'])

    query_type = 'children'
    go_term = "GO_0045120"
    distance = -1
    expected_keys = ['GO:0001939', 'GO:0001940']
    result_children = go.call(go_term, query_type)
    eq_([i['obo_id'] for i in result_children], expected_keys)
