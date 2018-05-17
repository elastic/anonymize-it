from abc import ABCMeta, abstractmethod
from elasticsearch import Elasticsearch, helpers
from elasticsearch_dsl import Search, A

class ESReaderError(Exception):
    pass


class BaseReader():
    def __init__(self, params, masked_fields, suppressed_fields):
        self.params = params
        self.masked_fields = masked_fields
        self.suppressed_fields = suppressed_fields

    @abstractmethod
    def get_data(self):
        pass


class ESReader(BaseReader):
    def __init__(self, params, masked_fields, suppressed_fields):
        super().__init__(params, masked_fields, suppressed_fields)
        self.host = self.params.get('host')
        self.un = self.params.get('username')
        self.pw = self.params.get('password')
        self.index_pattern = self.params.get('index')
        self.es = None

        if not all([self.host, self.un, self.pw]):
            raise ESReaderError("elasticsearch configuration malformed. please check config.")

        self.create_connection()
        self.create_mappings()
        self.get_data()

    def create_connection(self):
        self.es = Elasticsearch([self.host], http_auth = (self.un, self.pw), verify_certs=False)

    def create_mappings(self):
        mappings = {}
        for field, provider in self.masked_fields.items():
            print(field, provider)
            mappings[field] = {}
            s = Search(using=self.es, index=self.index_pattern)
            a = A('terms', field=field)
            s.aggs.bucket('unique', a)
            response = s.execute()
            for val in response['aggregations']['unique']['buckets']:
                mappings[field][val['key']] = None
        return mappings



    def get_data(self):
        pass


class CSVReader(BaseReader):
    def __init__(self, params):
        super().__init__(params)

    def get_data(self):
        pass


mapping = {
    "elasticsearch": ESReader,
    "csv": CSVReader
}

