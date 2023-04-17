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
                msg = "Received {} for url {}".format(request.status_code, url)
                raise ServiceError(msg)
        except (requests.ConnectionError, requests.HTTPError) as e:
            msg = "requests raised an error when trying to reach the " \
                "following url:\n{}".format(url)
            _log.error(msg)
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
                msg = "Received {} for url {}".format(request.status_code, url)
                raise ServiceError(msg)
        except (requests.ConnectionError, requests.HTTPError) as e:
            msg = "requests raised an error when trying to reach the " \
                "following url:\n{}".format(url)
            _log.error(msg)
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
                msg = "Received {} for url {}".format(request.status_code, url)
                _log.error("Couldn't get fasta from Uniprot: %s",
                           msg)
                raise ServiceError(msg)
        except (requests.ConnectionError, requests.HTTPError) as e:
            _log.error("Couldn't get fasta from Uniprot: %s", e)
            msg = "requests raised an error when trying to reach the " \
                "following url:\n{}".format(url)
            _log.error(msg)
            raise ServiceError(e)
        else:
            result = request.text
        return result
