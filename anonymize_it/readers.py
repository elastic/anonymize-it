from abc import ABCMeta, abstractmethod
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, A


class ESReaderError(Exception):
    pass


class BaseReader():
    def __init__(self, params, masked_fields, suppressed_fields):
        self.masked_fields = masked_fields
        self.suppressed_fields = suppressed_fields

    @abstractmethod
    def create_mappings(self):
        pass

    @abstractmethod
    def get_data(self, field_maps, suppressed_fields, include_all):
        pass


class ESReader(BaseReader):
    def __init__(self, params, masked_fields, suppressed_fields):
        super().__init__(params, masked_fields, suppressed_fields)

        # print(params)
        self.type = 'elasticsearch'
        self.host = params.get('host')
        self.username = params.get('username')
        self.password = params.get('password')
        self.index_pattern = params.get('index')
        self.query = params.get('query')
        self.es = None

        if not all([self.host, self.username, self.password]):
            raise ESReaderError("elasticsearch configuration malformed. please check config.")

        self.es = Elasticsearch([self.host], http_auth=(self.username, self.password), verify_certs=False)

    def create_mappings(self):
        mappings = {}
        for field, provider in self.masked_fields.items():
            mappings[field] = {}
            if provider:
                s = Search(using=self.es, index=self.index_pattern)
                if self.query:
                    s.update_from_dict({"query": self.query})
                a = A('terms', field=field, size=10000)
                s.aggs.bucket('unique', a)
                response = s.execute()
                for val in response['aggregations']['unique']['buckets']:
                    mappings[field][val['key']] = None
        return mappings

    def get_data(self, include, suppressed_fields, include_all=False):
        """

        :param field_maps:
        :param suppressed_fields:
        :param include_all:
        :return:
        """

        s = Search(using=self.es, index=self.index_pattern)
        if self.query:
            s.update_from_dict({"query": self.query})
        print(s.to_dict())
        if not include_all:
            s = s.source(include=include, exclude=suppressed_fields)
        else:
            s = s.source(exclude=suppressed_fields)

        response = s.scan()
        return response


class CSVReader(BaseReader):
    def __init__(self, params):
        super().__init__(params)

    def get_data(self, field_maps, suppressed_fields, include_all):
        pass


class PandasReader(BaseReader):
    def __init__(self, params):
        super().__init__(params)

    def get_data(self, field_maps, suppressed_fields, include_all):
        pass


reader_mapping = {
    "elasticsearch": ESReader,
    "csv": CSVReader,
    "pandas": PandasReader
}

