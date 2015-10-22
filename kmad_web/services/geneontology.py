import requests

from kmad_web.services.types import ServiceError


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
