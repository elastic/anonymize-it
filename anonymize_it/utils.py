import collections
import warnings
from itertools import islice, chain
import json
import faker

class ConfigParserError(Exception):
    pass


def flatten_nest(d, parent_key='', sep='.'):
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, collections.MutableMapping):
            items.extend(flatten_nest(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def parse_config(config):
    """first pass parsing of config file

    ensures that source and destination dicts exist, and sets types for reader and writer
    """
    source = config.get('source')
    dest = config.get('dest')
    masked_fields = config.get('include')
    suppressed_fields = config.get('exclude')
    include_rest = config.get('include_rest')

    if not source:
        raise ConfigParserError("source error: source not defined. Please check config.")
    if not dest:
        raise ConfigParserError("destination error: dest not defined. Please check config.")
    if not masked_fields:
        warnings.warn("no masked fields included in config. No data will be anonymized", Warning)

    reader_type = source.get('type')
    writer_type = dest.get('type')

    if not reader_type:
        raise ConfigParserError("source error: source type not defined. Please check config.")

    if not writer_type:
        raise ConfigParserError("destination error: dest type not defined. Please check config.")

    Config = collections.namedtuple('Config', 'source dest masked_fields suppressed_fields')
    config = Config(source, dest, masked_fields, suppressed_fields)
    return config


def batch(iterable, size):
    sourceiter = iter(iterable)
    while True:
        batchiter = islice(sourceiter, size)
        yield chain([next(batchiter)], batchiter)


def faker_examples():
    providers = []
    examples = []
    f = faker.Faker()
    for provider in dir(faker.providers):
        if provider[0].islower():
            if provider == 'misc':
                continue
            try:
                for fake in dir(getattr(faker.providers, provider).Provider):
                    if fake[0].islower():
                        for i in range(5):
                            try:
                                examples.append(str(getattr(f, fake)()))
                                providers.append(fake)
                            except Exception as e:
                                print(e)
                                continue
            except:
                continue
    return providers, examples


def composite_query(field, size, query=None, term=""):
    body= {
        "size": 0,
        "aggs": {
            "my_buckets": {
                "composite": {
                    "size": size,
                    "sources" : [
                        {field: {"terms": {"field": field}}}
                    ],
                    "after": {field: term}
                }
            }
        }
    }
    if query:
        body['query'] = query
    return json.dumps(body)