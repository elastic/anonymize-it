from abc import abstractmethod, ABCMeta
import json

class BaseWriter():
    def __init__(self, params):
        self.params = params

    @abstractmethod
    def write_data(self, data):
        pass


class ESWriter(BaseWriter):
    def __init__(self, params):
        super().__init__(params)


class FSWriter(BaseWriter):
    def __init__(self, params):
        super().__init__(params)
        self.out_dir = self.params.get('directory')

    def write_data(self, data):
        with open("{}/output.json".format(self.out_dir), 'w') as f:
            json.dump(data, f)


mapping = {
    "elasticsearch": ESWriter,
    "filesystem": FSWriter
}