import os
import requests

from kmad_web.services.types import ServiceError


class UniprotService(object):
    def __init__(self, url=None):
        self._url = url

    @property
    def url(self):
        return self._url

    @url.setter
    def url(self, url):
        self._url = url

    def get_txt(self, uniprot_id):
        try:
            url = os.path.join(self._url, uniprot_id + ".txt")
            request = requests.get(url)
            if request.status_code != 200:
                raise ServiceError(request.status_code)
        except requests.HTTPError as e:
                raise ServiceError(e)
        else:
            result = request.text
        return result

    def get_fasta(self, uniprot_id):
        try:
            url = os.path.join(self._url, uniprot_id + ".fasta")
            request = requests.get(url)
            if request.status_code != 200:
                raise ServiceError(request.status_code)
        except requests.HTTPError as e:
                raise ServiceError(e)
        else:
            result = request.text
        return result

uniprot = UniprotService()
