import re

from kmad_web.default_settings import GO_URL
from kmad_web.services.go import GoService
from kmad_web.services.types import ServiceError


class GoProvider(object):
    def __init__(self):
        self.children = set()
        self.parents = set()
        self._go_reg = re.compile("^GO_[0-9]{7}$")

    def get_parent_terms(self, go_term):
        go = GoService(GO_URL)
        query = 'parents'

        if not go_term.startswith('GO'):
            go_term = "GO_" + go_term
        else:
            go_term = go_term.replace(":", "_")
        assert self._go_reg.match(go_term)
        try:
            response = go.call(go_term, query)
            self.parents = set([term['obo_id'] for term in response])
        except ServiceError:
            pass

    def get_children_terms(self, go_term):
        go = GoService(GO_URL)
        query = 'descendants'
        if not go_term.startswith('GO'):
            go_term = "GO_" + go_term
        else:
            go_term = go_term.replace(":", "_")
        assert self._go_reg.match(go_term)

        try:
            response = go.call(go_term, query)
            self.children = set([term['obo_id'] for term in response])
        except ServiceError:
            pass
