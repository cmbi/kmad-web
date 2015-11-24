import logging

from kmad_web.services.types import ServiceError
from kmad_web.services.helpers import soap
from kmad_web.services.helpers.cache import cache_manager as cm

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

    @cm.cache('redis')
    def call(self, method, *args, **kwargs):
        _log.info("Calling go search method '{}'".format(method))
        if self._url is None:
            _log.error("Goservice hasn't been configured")
            raise ServiceError("GoService hasn't been configured")

        if 'soap_timeout' not in kwargs:
            soap_timeout = 100
        return soap.run(self._url, soap_timeout, method, *args)
