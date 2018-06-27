from abc import abstractmethod, ABCMeta
import json
import uuid
import os

from google.oauth2 import service_account
from google.cloud import storage


class BaseWriter(metaclass=ABCMeta):
    def __init__(self, params):
        self.type = params.get('type')

    @abstractmethod
    def write_data(self, data, file_name=None):
        pass


class ESWriter(BaseWriter):
    def __init__(self, params):
        super().__init__(params)


class FSWriter(BaseWriter):
    def __init__(self, params):
        super().__init__(params)
        self.type = 'filesystem'
        self.out_dir = params.get('directory')

    def write_data(self, data, file_name=None):
        if not file_name:
            file_name = str(uuid.uuid4())
        with open("{}/{}.json".format(self.out_dir, file_name), 'w') as f:
            f.write("\n".join(data))


class GCSWriter(BaseWriter):
    def __init__(self, params):
        super().__init__(params)
        self.type = 'gcs'
        self.bucket = params.get('bucket')
        self.credentials = params.get('credentials')
        self.out_dir = params.get('dir_pattern')

        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = self.credentials
        self.client = storage.Client()
        self.bucket = self.client.get_bucket(self.bucket)

    def write_data(self, data, file_name=None):
        if not file_name:
            file_name = str(uuid.uuid4())
        blob = self.bucket.blob('{}{}'.format(self.out_dir, file_name))
        blob.upload_from_string("\n".join(data))



writer_mapping = {
    "elasticsearch": ESWriter,
    "filesystem": FSWriter,
    "gcs": GCSWriter
}