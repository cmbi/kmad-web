import urllib2

from socket import error as SocketError
from httplib import BadStatusLine

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
        req = urllib2.Request(self._url)
        try:
            response = urllib2.urlopen(req)
        except (urllib2.HTTPError,  urllib2.URLError,
                SocketError, BadStatusLine) as e:
            raise ServiceError(e)
        else:
            result = response.read()
        return result

elm = ElmService()
