import collections
import warnings
from itertools import islice, chain
import json
import faker

try:
    # Import ABC from collections.abc for Python 3.4+
    from collections.abc import MutableMapping
except ImportError:
    # Fallback for Python 2
    from collections import MutableMapping


class ConfigParserError(Exception):
    pass


def flatten_nest(d, parent_key='', sep='.'):
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, MutableMapping):
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
    sensitive = config.get('sensitive')

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

    Config = collections.namedtuple('Config', 'source dest masked_fields suppressed_fields include_rest sensitive')
    config = Config(source, dest, masked_fields, suppressed_fields, include_rest, sensitive)
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


def contains_secret(regexes, field_value):
    if type(field_value) == list:
        for f in field_value:
            if any([regex.search(f) for regex in regexes]):
                return True
    elif any([regex.search(field_value) for regex in regexes]):
            return True


def composite_query(field, size, query=None, term=""):
    body= {
            "size": 0,
            "aggs": {
                "my_buckets": {
                    "composite": {
                        "size": size,
                        "sources" : [
                            {field: {"terms": {"field": field}}}
                        ]
                    }
                }
            }
        }
    if term:
        body["aggs"]["my_buckets"]["composite"]["after"] = {field: term}
    if query:
        body['query'] = query
    return json.dumps(body)
