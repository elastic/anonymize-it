class BaseWriter():
    def __init__(self, params):
        self.params = params


class ESWriter(BaseWriter):
    def __init__(self):
        super().__init__()


class FSWriter(BaseWriter):
    def __init__(self, params):
        super().__init__(params)


mapping = {
    "elasticsearch": ESWriter,
    "filesystem": FSWriter
}