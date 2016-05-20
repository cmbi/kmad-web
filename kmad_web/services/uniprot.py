import logging
import os
import requests

from kmad_web.services.types import ServiceError
from kmad_web.services.helpers.cache import cache_manager as cm

_log = logging.getLogger(__name__)


class UniprotService(object):
    def __init__(self, url=None):
        self._url = url

    @property
    def url(self):
        return self._url

    @url.setter
    def url(self, url):
        self._url = url

    @cm.cache('redis')
    def get_xml(self, uniprot_id):
        _log.debug("Getting txt data from Uniprot for uniprot id %s",
                   uniprot_id)
        try:
            url = os.path.join(self._url, uniprot_id + ".xml")
            request = requests.get(url)
            if request.status_code != 200:
                raise ServiceError(request.status_code)
        except (requests.ConnectionError, requests.HTTPError) as e:
            raise ServiceError(e)
        else:
            result = request.text
        return result

    @cm.cache('redis')
    def get_txt(self, uniprot_id):
        _log.debug("Getting txt data from Uniprot for uniprot id %s",
                   uniprot_id)
        try:
            url = os.path.join(self._url, uniprot_id + ".txt")
            request = requests.get(url)
            if request.status_code != 200:
                raise ServiceError(request.status_code)
        except (requests.ConnectionError, requests.HTTPError) as e:
            raise ServiceError(e)
        else:
            result = request.text
        return result

    @cm.cache('redis')
    def get_fasta(self, uniprot_id):
        _log.debug("Getting fasta from Uniprot for uniprot id %s", uniprot_id)
        try:
            url = os.path.join(self._url, uniprot_id + ".fasta")
            request = requests.get(url)
            if request.status_code != 200:
                _log.error("Couldn't get fasta from Uniprot: %s",
                           request.status_code)
                raise ServiceError(request.status_code)
        except (requests.ConnectionError, requests.HTTPError) as e:
            _log.error("Couldn't get fasta from Uniprot: %s", e)
            raise ServiceError(e)
        else:
            result = request.text
        return result
