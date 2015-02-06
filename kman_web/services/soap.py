import logging

from suds.client import Client
from suds.sudsobject import asdict, Object
from suds.sax.text import Text


__all__ = ['run']


# By default the suds logger outputs debug messages, which floods the console.
logging.getLogger('suds').setLevel(logging.INFO)
_log = logging.getLogger(__name__)


# http://stackoverflow.com/questions/2412486/serializing-a-suds-object-in-python
def recursive_asdict(d):
    """Convert Suds object into serializable format."""
    out = {}
    for k, v in asdict(d).iteritems():
        if hasattr(v, '__keylist__'):
            out[k] = recursive_asdict(v)
        elif isinstance(v, list):
            out[k] = []
            for item in v:
                if hasattr(item, '__keylist__'):
                    out[k].append(recursive_asdict(item))
                else:
                    out[k].append(item)
        else:
            out[k] = v
    return out


def run(url, timeout, method, *args):
    client = Client(url, faults=True, timeout=timeout)

    _log.info("Running '{}' on url '{}'".format(method, url))
    response = getattr(client.service, method)(*args)
    _log.info("Finished running '{}' on url '{}'".format(method, url))

    if isinstance(response, Object):
        return recursive_asdict(response)
    elif isinstance(response, Text):
        return str(response)
    elif isinstance(response, list):
        return [recursive_asdict(r) for r in response]
    else:
        return response

    return response
