from abc import abstractmethod, ABCMeta
import json
import uuid
import os

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
            json.dump(data, f)


writer_mapping = {
    "elasticsearch": ESWriter,
    "filesystem": FSWriter
}