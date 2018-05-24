from faker import Faker
import warnings
import readers
import writers
import utils


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

        self.field_maps = field_maps
        self.reader = reader
        self.writer = writer

        self.source = None
        self.dest = None
        self.masked_fields = None
        self.suppressed_fields = None
        self.reader_type = None
        self.writer_type = None
        self.include_rest = None

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

    def anonymize(self):
        """this is the core method for anonymizing data

        it utilizes specific reader and writer class methods to retrieve and store data. in the process
        we define mappings of unmasked values to masked values, and anonymize fields using self.faker
        """

        # first, create masking maps that will be used for lookups when anonymizing data
        self.field_maps = self.reader.create_mappings()
        for field, map in self.field_maps.items():
            for value, _ in map.items():
                mask_str = self.reader.masked_fields[field]
                mask = self.provider_map[mask_str]
                map[value] = mask()

        # get generator object from reader
        data = self.reader.get_data(list(self.field_maps.keys()), self.suppressed_fields, self.include_rest)

        # batch process the data and write out to json in chunks
        for batchiter in utils.batch(data, 10000):
            tmp = []
            for item in batchiter:
                item = utils.flatten_nest(item.to_dict())
                for field, v in self.field_maps.items():
                    if v:
                        item[field] = self.field_maps[field][item[field]]
                        tmp.append(utils.flatten_nest(item))
            self.writer.write_data(tmp)
