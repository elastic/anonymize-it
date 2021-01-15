from faker import Faker
import warnings
from . import readers
from . import writers
from . import utils
import re
import json
import logging
import os
class AnonymizerError(Exception):
    pass


class ReaderError(Exception):
    pass


class WriterError(Exception):
    pass


class Anonymizer:
    def __init__(self, reader=None, writer=None, field_maps={}):
        """a prepackaged anonymizer class

        an anonymizer is responsible for grabbing data from the source datastore,
        masking fields specified in a config, and writing data to a destination

        can be used by

        :param reader: an instantiated reader
        :param writer: an instantiated writer
        :param field_maps: a dict like {'field.name': 'mapping_type'}
        """
        self.faker = Faker()

        # add provider mappings here. these should map strings from the config to Faker providers
        self.provider_map = {
            "file_path": self.faker.file_path,
            "ipv4": self.faker.ipv4
        }

        # add high cardinality fields
        self.high_cardinality_fields = {}

        # add user info regexes
        self.user_regexes = {}

        # drop documents if they contain these keywords
        self.keywords = []

        self.dir_path = os.path.abspath(os.path.dirname(__file__))
        with open(os.path.join(self.dir_path, "secret_regexes.json"), "r") as f:
            self.secret_regexes = json.load(f)

        self.field_maps = field_maps
        self.reader = reader
        self.writer = writer

        self.source = None
        self.dest = None
        self.masked_fields = None
        self.suppressed_fields = None
        self.reader_type = None
        self.writer_type = None

        # only parse config if it exists
        # this allows for anonymizer class instantiation via direct parameter setting
        if not self.reader:
            self.instantiate_reader()
        if not self.writer:
            self.instantiate_writer()

        # if used programmatically, an anonymizer must be instantiated with a reader and a writer
        elif not all([self.reader, self.writer]):
            raise AnonymizerError("Anonymizers must include both a reader and a writer")

    def instantiate_reader(self):
        source_params = self.source.get('params')
        if not source_params:
            raise ReaderError("source params not defined: please check config")

        reader = readers.mapping.get(self.reader_type)
        if not reader:
            raise ReaderError("No reader named {} defined.".format(self.reader_type))

        self.reader = reader(source_params, self.masked_fields, self.suppressed_fields)

    def instantiate_writer(self):
        dest_params = self.dest.get('params')
        if not dest_params:
            raise WriterError("dest params not define: please check config")

        writer = writers.mapping.get(self.writer_type)
        if not writer:
            raise WriterError("No writer named {} defined.".format(self.writer_type))

        self.writer = writer(dest_params)

    def anonymize(self, sensitive_fields=[], infer=False, include_rest=False):
        """this is the core method for anonymizing data

        it utilizes specific reader and writer class methods to retrieve and store data. in the process
        we define mappings of unmasked values to masked values, and anonymize fields using self.faker
        """

        # first, infer mappings based on indices and overwrite the config.
        if infer:
            self.reader.infer_providers()

        # next, create masking maps that will be used for lookups when anonymizing data
        self.field_maps = self.reader.create_mappings()

        for field, map in self.field_maps.items():
            for value, _ in map.items():
                mask_str = self.reader.masked_fields[field]
                if mask_str != 'infer':
                    if mask_str not in self.high_cardinality_fields:
                        mask = self.provider_map[mask_str]
                        map[value] = mask()

        # get generator object from reader
        total = self.reader.get_count()
        logging.info("total number of records {}...".format(total))

        data = self.reader.get_data(include_rest)

        all_users_regex = re.compile('|'.join([regex for regex in self.user_regexes.values()]), flags=re.MULTILINE|re.IGNORECASE)

        all_secrets_regex = re.compile('|'.join([regex for regex in self.secret_regexes.values()]))

        # batch process the data and write out to json in chunks
        count = 0
        for batchiter in utils.batch(data, 10000):
            tmp = []
            for item in batchiter:
                bulk = {
                    "index": {
                        "_index": item.meta['index'],
                        "_type": 'doc'
                    }
                }
                #tmp.append(json.dumps(bulk))
                item = utils.flatten_nest(item.to_dict())
                contains_keywords = False
                for field in list(item):
                    if self.high_cardinality_fields.get(field):
                        item[field] = self.high_cardinality_fields[field][item[field] % len(self.high_cardinality_fields[field])]
                    elif self.field_maps.get(field, None):
                        if type(item[field]) == list:
                            # Since this is a list we need to sub out every item
                            item[field] = [self.field_maps[field].get(f, "This should not happen (list)!!!") for f in item[field]]
                        else:
                            item[field] = self.field_maps[field].get(item[field], "This should not happen!!!")

                    if field in sensitive_fields:
                        if field in self.field_maps or field in self.high_cardinality_fields:
                            raise AnonymizerError("Sensitive fields should not be anonymized using faker providers")

                        # Don't proceed if any field contains keywords
                        if utils.contains_keywords(item[field], self.keywords):
                            contains_keywords = True
                            break
                        # Remove the field if it contains a secret
                        if utils.contains_secret(all_secrets_regex, item[field]):
                            del item[field]
                            continue
                        # Remove user information from fields
                        if type(item[field]) == list:
                            item[field] = [re.sub(all_users_regex, r"\1", f) for f in item[field]]
                        else:
                            item[field] = re.sub(all_users_regex, r"\1", item[field])
                if not contains_keywords:
                    tmp.append(json.dumps(utils.flatten_nest(item)))
            self.writer.write_data(tmp)
            count += len(tmp)
            #count += len(tmp) / 2# There is a bulk row for every document
            logging.info("{} % complete...".format(count/total * 100))
