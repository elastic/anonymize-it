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
    file_name = "output"
    fswriter.write_data(data, file_name=file_name)
    dir_path = os.path.join(os.path.abspath(os.getcwd()), fswriter.out_dir)
    with open(f'{dir_path}/{file_name}.json', 'r') as f:
        in_data = json.load(f)

    os.remove(file_name)

    assert data == in_data


def test_ESWriter():
    pass
