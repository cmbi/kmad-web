import logging
import requests
import time
import xmltodict
from xml.parsers.expat import ExpatError

from kmad_web.services.types import ServiceError, TimeoutError
from kmad_web.services.helpers.cache import cache_manager as cm

_log = logging.getLogger(__name__)


class PfamService(object):
    def __init__(self, url=None):
        self._url = url

    @property
    def url(self):
        return self._url

    @url.setter
    def url(self, url):
        self._url = url

    @cm.cache('redis')
    def search(self, fasta_sequence, timeout=7200, poll=7):
        _log.info("Running Pfam search: {}".format(fasta_sequence))
        if self._url is None:
            raise ServiceError("PfamService hasn't been configured")
        result_url = self._create(fasta_sequence)
        start_time = time.time()
        while True:
            r = self._status(result_url)
            if r['status'] == "SUCCESS":
                return r['result']
            else:
                now = time.time()
                if now - start_time > timeout:
                    raise TimeoutError("Pfam took too long")
                time.sleep(poll)

    def _create(self, fasta_sequence):
        try:
            data = {'seq': fasta_sequence, 'output': 'xml'}
            request = requests.post(self._url, data=data)
            request.raise_for_status()
        except requests.HTTPError as e:
                raise ServiceError(e)
        else:
            try:
                result = xmltodict.parse(request.text)
                result_url = result['jobs']['job']['result_url']
            except (KeyError, ExpatError) as e:
                raise ServiceError(
                    "{}\nUnexpected response from Pfam".format(e.message))
        return result_url

    def _status(self, url):
        try:
            request = requests.get(url)
            request.raise_for_status()
        except requests.HTTPError as e:
            raise ServiceError(e)
        else:
            # The Pfam service returns XML when the result is ready, otherwise
            # it returns HTML
            # The content-type isn't being set correctly so we can't check it
            if request.text.startswith("<?xml"):
                status = "SUCCESS"
            else:
                status = "PENDING"
            return {"status": status, "result": request.text}
