import logging

from dogpile.cache import make_region


__all__ = ['cache_manager']


_log = logging.getLogger(__name__)


class CacheManager(object):
    def __init__(self, config=None):
        self.regions = {}
        if config is not None:
            self.load_config(config)

    def load_config(self, config):
        for region, config in config.iteritems():
            self.regions[region] = make_region().configure_from_config(
                config, '{}.'.format(region))

    def reset(self):
        self.regions = {}

    def cache(self, name):
        def wrapped(f):
            def new_f(*args, **kwargs):
                if self.regions == {}:
                    raise ValueError("CacheManager hasn't been configured")

                if name not in self.regions:
                    raise ValueError("'{}' is not a valid cache".format(name))

                region = self.regions[name]
                assert region is not None

                region_decorator = region.cache_on_arguments()

                return region_decorator(f)(*args, **kwargs)
            new_f.__name__ = f.__name__
            return new_f
        return wrapped


cache_manager = CacheManager()
