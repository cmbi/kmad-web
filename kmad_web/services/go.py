import logging
import requests

from kmad_web.services.types import ServiceError
# from kmad_web.services.helpers import soap
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
    def call(self, go_term, query_type):
        _log.info("Calling go search method '{}'".format(query_type))
        if self._url is None:
            _log.error("Goservice hasn't been configured")
            raise ServiceError("GoService hasn't been configured")
        url = "{}{}/{}".format(self._url, go_term, query_type)
        try:
            request = requests.get(url, data={"Accept": "application/json"})
            if request.status_code != 200:
                    raise ServiceError(request.status_code)
        except (requests.ConnectionError, requests.HTTPError) as e:
            msg = "requests raised an error when trying to reach the " \
                "following url:\n{}".format(url)
            _log.error(msg)
            raise ServiceError(e)
        else:
            result = request.json()['_embedded']['terms']
        return result
