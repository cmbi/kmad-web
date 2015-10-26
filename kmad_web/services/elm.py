import os
import requests

from lxml import html

from kmad_web.services.types import ServiceError


class ElmService(object):
    def __init__(self, url=None):
        self._url = url

    @property
    def url(self):
        return self._url

    @url.setter
    def url(self, url):
        self._url = url

    def get_instances(self, uniprot_id):
        try:
            url = os.path.join(self._url,
                               "instances.gff?q={}".format(uniprot_id))
            request = requests.get(url)
            if request.status_code != 200:
                raise ServiceError(request.status_code)
        except requests.HTTPError as e:
                raise ServiceError(e)
        else:
            result = request.text
        return result

    def get_all_classes(self):
        try:
            url = os.path.join(self._url, "elms_index.tsv")
            request = requests.get(url)
            if request.status_code != 200:
                raise ServiceError(request.status_code)
        except requests.HTTPError as e:
                raise ServiceError(e)
        else:
            result = request.text
        return result
    
    def get_motif_go_terms(self, motif_id):
        url = os.path.join(self._url, 'elms/{}.html'.format(motif_id))
        page = requests.get(url)
        tree = html.fromstring(page.text)
        go_terms = []
        for i in tree.get_element_by_id('ElmDetailGoterms').iterlinks():
            if i[2].startswith("http://www.ebi.ac.uk/QuickGO/GTerm?id=GO:"):
                go_terms += [i[2].split(':')[2]]
        return go_terms
