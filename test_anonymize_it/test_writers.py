from anonymize_it import writers
import json
import os


def test_fswriter():
    params = {
        "directory": "test_output"
    }

    data = {
        "test": "this is a test".split()
    }

    fswriter = writers.FSWriter(params)
    fswriter.write_data(data)
    file_name = "test_output/output.json"
    with open(file_name, 'r') as f:
        in_data = json.load(f)

    os.remove(file_name)

    assert data == in_data


def test_ESWriter():
    pass