import sys
import json
from anonymizers import Anonymizer
from readers import reader_mapping
from writers import writer_mapping
import utils
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def read_config(config_file):
    with open(config_file, 'r') as f:
        config = json.load(f)
    return config


if __name__ == "__main__":
    config_file = sys.argv[1]
    config = read_config(config_file)
    config = utils.parse_config(config)

    print("Configuration:\n\t", config)

    reader = reader_mapping[config.source['type']]
    reader = reader(config.source['params'], config.masked_fields, config.suppressed_fields)

    writer = writer_mapping[config.dest['type']]
    writer = writer(config.dest['params'])

    anon = Anonymizer(reader=reader, writer=writer)
    anon.anonymize()
