import logging
import requests
import time
import xmltodict
from xml.parsers.expat import ExpatError

from kmad_web.services.types import ServiceError, TimeoutError
from kmad_web.services.helpers.cache import cache_manager as cm

_log = logging.getLogger(__name__)


class PfamService(object):
    def __init__(self, url=None, ID_URL_CREATE=None):
        self._url = url
        self._ID_URL_CREATE = ID_URL_CREATE

    @property
    def url(self):
        return self._url

    @url.setter
    def url(self, url):
        self._url = url

    @cm.cache('redis')
    def get_by_id(self, uniprot_id):
        _log.info("Getting Pfam result for id {}".format(uniprot_id))
        try:
            url = self._ID_URL_CREATE.format(uniprot_id)
            request = requests.get(url)
            request.raise_for_status()
            if request.text.startswith("<?xml"):
                _log.info("Found a Pfam result for id {}".format(uniprot_id))
                return request.text
            else:
                return None
        except (requests.ConnectionError, requests.HTTPError) as e:
            _log.info("Pfam error: {}".format(e))
            return None

    @cm.cache('redis')
    def search(self, fasta_sequence, timeout=1200, poll=7):
        _log.info("Running Pfam search")
        if self._url is None:
            raise ServiceError("PfamService hasn't been configured")
        result_url = self._create(fasta_sequence)
        start_time = time.time()
        while True:
            r = self._status(result_url)
            if (r['status'] == "SUCCESS"
                    and not r['result'].startswith('<error>')):
                return r['result']
            elif r['result'].startswith('<error>'):
                _log.info("Pfam returned an error: {}".format(r['result']))
                raise ServiceError("Pfam service returned an error")
            else:
                now = time.time()
                if now - start_time > timeout:
                    _log.info("Pfam raised a TimeoutError")
                    raise TimeoutError("Pfam took too long")
                time.sleep(poll)

    def _create(self, fasta_sequence):
        try:
            data = {'seq': fasta_sequence, 'output': 'xml'}
            _log.debug("Submitting sequence:\n{}".format(fasta_sequence))
            request = requests.post(self._url, data=data)
            request.raise_for_status()
        except (requests.ConnectionError, requests.HTTPError) as e:
            _log.info("Pfam returned an error: {}".format(e))
            raise ServiceError(e)
        else:
            try:
                result = xmltodict.parse(request.text)
                result_url = result['jobs']['job']['result_url']
            except (KeyError, ExpatError) as e:
                _log.info("Pfam returned an error: {}".format(e))
                raise ServiceError(
                    "{}\nUnexpected response from Pfam".format(e.message))

        return result_url

    def _status(self, url):
        try:
            request = requests.get(url)
            request.raise_for_status()
        except (requests.ConnectionError, requests.HTTPError) as e:
            raise ServiceError(e)
        else:
            # The Pfam service returns XML when the result is ready, otherwise
            # it returns HTML
            # The content-type isn't being set correctly so we can't check it
            if request.text.startswith("<?xml"):
                status = "SUCCESS"
            else:
                status = "PENDING"
            _log.debug("Pfam status: {}".format(status))
            _log.debug("Pfam response: {}".format(request.text))
            return {"status": status, "result": request.text}
