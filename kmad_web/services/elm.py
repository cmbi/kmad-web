import logging
import os
import re
import requests

from BeautifulSoup import BeautifulSoup

from kmad_web.services.types import ServiceError
from kmad_web.services.helpers.cache import cache_manager as cm

_log = logging.getLogger(__name__)


class ElmService(object):
    def __init__(self, url=None):
        self._url = url

    @property
    def url(self):
        return self._url

    @url.setter
    def url(self, url):
        self._url = url

    @cm.cache('redis')
    def get_instances(self, uniprot_id):
        _log.info("Getting motif instances from ELM for uniprot id: {}".format(
            uniprot_id
        ))
        try:
            url = os.path.join(self._url,
                               "instances.gff?q={}".format(uniprot_id))
            request = requests.get(url)
            if request.status_code != 200:
                _log.error("ELM returned an error: {}".format(
                    request.status_code))
                raise ServiceError(request.status_code)
        except requests.HTTPError as e:
            _log.error("ELM returned an error: {}".format(e))
            raise ServiceError(e)
        else:
            result = request.text
        return result

    def get_all_classes(self):
        _log.info("Getting all motif classes from ELM")
        try:
            url = os.path.join(self._url, "elms", "elms_index.tsv")
            request = requests.get(url)
            if request.status_code != 200:
                _log.error("ELM returned an error: {}".format(
                    request.status_code))
                raise ServiceError(request.status_code)
        except requests.HTTPError as e:
            _log.error("ELM returned an error: {}".format(e))
            raise ServiceError(e)
        else:
            result = request.text
        return result

    @cm.cache('redis')
    def get_motif_go_terms(self, motif_id):
        _log.info("Getting GO terms for motif {}".format(
            motif_id
        ))
        url = os.path.join(self._url, 'elms/{}.html'.format(motif_id))
        try:
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
        except requests.HTTPError as e:
            _log.error("ELM returned an error: {}".format(e))
            raise ServiceError(e)
