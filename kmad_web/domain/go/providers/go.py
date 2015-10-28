from kmad_web.default_settings import GO_URL
from kmad_web.services.go import GoService


class GoProvider(object):
    def __init__(self):
        self.children = set()
        self.parents = set()

    def get_parent_terms(self, go_term):
        go = GoService(GO_URL)
        method = 'getTermParents'
        self.parents = set(go.call(method, go_term, "GO"))

    def get_children_terms(self, go_term):
        go = GoService(GO_URL)
        method = 'getTermChildren'
        # distance < 0 to get all children
        distance = -1
        self.children = set(go.call(method, go_term, "GO", distance))
