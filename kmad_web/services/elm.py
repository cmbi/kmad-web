import os
import re
import requests

from BeautifulSoup import BeautifulSoup

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
            url = os.path.join(self._url, "elms", "elms_index.tsv")
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
        page = requests.get(url).text
        soup = BeautifulSoup(page)
        goterms_div = soup.find('div', {'id': 'ElmDetailGoterms'})
        go_terms = set()
        if goterms_div:
            # need to get all links from the ElmDetailGoterms div
            # - the GO term is extarcted from the link's url
            links = goterms_div.findAll('a')
            reg = re.compile('GTerm\?id=GO:(?P<go_term>[0-9]{7})')
            for l in links:
                for match in reg.finditer(str(l)):
                    go_terms.add(match.groupdict('')['go_term'])
        else:
            print "No GO terms found for motif: {}".format(motif_id)
        return go_terms
