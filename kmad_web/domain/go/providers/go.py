import re

from kmad_web.default_settings import GO_URL
from kmad_web.services.go import GoService


class GoProvider(object):
    def __init__(self):
        self.children = set()
        self.parents = set()
        self._go_reg = re.compile("^GO:[0-9]{7}$")

    def get_parent_terms(self, go_term):
        go = GoService(GO_URL)
        method = 'getTermParents'

        if not go_term.startswith('GO:'):
            go_term = "GO:" + go_term
        assert self._go_reg.match(go_term)

        response = dict(go.call(method, go_term, "GO"))
        if response:
            self.parents = set([str(g['key']) for g in response['item']])

    def get_children_terms(self, go_term):
        go = GoService(GO_URL)
        method = 'getTermChildren'
        if not go_term.startswith('GO:'):
            go_term = "GO:" + go_term
        assert self._go_reg.match(go_term)

        # distance < 0 to get all children
        distance = -1
        response = dict(go.call(method, go_term, "GO", distance))
        if response:
            self.children = set([g['key'] for g in response['item']])
