from abc import ABCMeta, abstractmethod
from faker import Faker
import warnings
import readers
import writers
import utils

class ConfigParserError(Exception):
    pass

class ReaderError(Exception):
    pass

class WriterError(Exception):
    pass

class Anonymizer(metaclass=ABCMeta):
    def __init__(self, config):
        """a prepackaged anonymizer class

        an anonymizer is responsible for grabbing data from the source datastore,
        masking fields specified in a config, and writing data to a destination

        :param config: a configuration dict
        """
        self.faker = Faker()

        # add provider mappings here. these should map strings from the config to Faker providers
        self.provider_map = {
            "file_path": self.faker.file_path,
            "ipv4": self.faker.ipv4
        }

        self.config = config
        self.source = None
        self.dest = None
        self.masked_fields = None
        self.suppressed_fields = None
        self.reader_type = None
        self.writer_type = None
        self.reader = None
        self.writer = None
        self.include_rest = None
        self.field_maps = {}

        self.parse_config()
        self.instantiate_reader()
        self.instantiate_writer()

        self.anonymize()

    def parse_config(self):
        """first pass parsing of config file

        ensures that source and destination dicts exist, and sets types for reader and writer
        """
        self.source = self.config.get('source')
        self.dest = self.config.get('dest')
        self.masked_fields = self.config.get('include')
        self.suppressed_fields = self.config.get('exclude')
        self.include_rest = self.config.get('include_rest')

        if not self.source:
            raise ConfigParserError("source error: source not defined. Please check config.")
        if not self.dest:
            raise ConfigParserError("destination error: dest not defined. Please check config.")
        if not self.masked_fields:
            warnings.warn("no masked fields included in config. No data will be anonymized", Warning)

        print("Masking Fields\n{}".format(self.masked_fields))
        print("Suppressing Fields\n{}".format("\n".join(self.suppressed_fields)))

        self.reader_type = self.source.get('type')
        self.writer_type = self.dest.get('type')

        if not self.reader_type:
            raise ConfigParserError("source error: source type not defined. Please check config.")

        if not self.writer_type:
            raise ConfigParserError("destination error: dest type not defined. Please check config.")

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

    def anonymize(self):
        """this is the core method for anonymizing data

        it utilizes specific reader and writer class methods to retrieve and store data. in the process
        we define mappings of unmasked values to masked values, and anonymize fields using self.faker
        """

        # first, create masking maps that will be used for lookups when anonymizing data
        self.field_maps = self.reader.create_mappings()
        for field, map in self.field_maps.items():
            for value, _ in map.items():
                mask_str = self.masked_fields[field]
                mask = self.provider_map[mask_str]
                map[value] = mask()

        # read data in data object
        self.data = self.reader.get_data(list(self.field_maps.keys()), self.suppressed_fields, self.include_rest)
        self.data = [utils.flatten(obj) for obj in self.data]

        # anonymize the values
        for field, v in self.field_maps.items():
            if v:
                for event in self.data:
                    event[field] = self.field_maps[field][event[field]]

        # write
        self.writer.write_data(self.data)
