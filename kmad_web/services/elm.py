import urllib2


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
        print self._url
        print self.url
        req = urllib2.Request(self._url)
        response = urllib2.urlopen(req)
        result = response.read()
        return result

elm = ElmService()
