from nose.tools import eq_
from kmad_web.domain.go.providers.go import GoProvider


def test_get_children_terms():

    go_term = 'GO:0070137'

    expected = set(['GO:0070139'])

    go = GoProvider()
    go.get_children_terms(go_term)
    eq_(expected, go.children)

    go_term = '0070137'
    go.get_children_terms(go_term)
    eq_(expected, go.children)


def test_get_parent_terms():

    go_term = 'GO:0070139'

    expected = set(['GO:0070137', 'GO:0016929'])

    go = GoProvider()
    go.get_parent_terms(go_term)
    eq_(expected, go.parents)

    go_term = '0070139'
    go.get_parent_terms(go_term)
    eq_(expected, go.parents)
