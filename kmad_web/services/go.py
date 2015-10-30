import logging
import requests

from kmad_web.services.types import ServiceError
from kmad_web.services.helpers import soap

logging.basicConfig()
_log = logging.getLogger(__name__)


class GoService(object):
    def __init__(self, url=None):
        self._url = url
        self._go_terms = []

    @property
    def url(self):
        return self._url

    @url.setter
    def url(self, url):
        self._url = url

    def get_go_terms(self):
        try:
            request = requests.get(self._url)
            if request.status_code != 200:
                raise ServiceError(request.status_code)
        except requests.HTTPError as e:
                raise ServiceError(e)
        else:
            self._go_terms = request.text

    def call(self, method, *args, **kwargs):
        _log.info("Calling go search method '{}'".format(method))
        if self._url is None:
            raise ServiceError("GoService hasn't been configured")

        if 'soap_timeout' not in kwargs:
            soap_timeout = 100
        return soap.run(self._url, soap_timeout, method, *args)
