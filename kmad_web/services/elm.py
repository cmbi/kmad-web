import os
import requests

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
        try:
            url = os.path.join(self._url,
                               "instances.gff?q={}".format(uniprot_id))
            request = requests.get(url)
            if request.status_code != 200:
                raise ServiceError(request.status_code)
        except requests.HTTPError as e:
                raise ServiceError(e)
        else:
            result = request.text
        return result

    def get_all_classes(self):
        try:
            url = os.path.join(self._url, "elms_index.tsv")
            request = requests.get(url)
            if request.status_code != 200:
                raise ServiceError(request.status_code)
        except requests.HTTPError as e:
                raise ServiceError(e)
        else:
            result = request.text
        return result

elm = ElmService()
