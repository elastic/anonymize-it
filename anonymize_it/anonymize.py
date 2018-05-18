import sys
import json
from anonymizers import Anonymizer
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def read_config(config_file):
    with open(config_file, 'r') as f:
        config = json.load(f)
    return config


def anonymize():
    pass


if __name__ == "__main__":
    config_file = sys.argv[1]
    config = read_config(config_file)
    anon = Anonymizer(config)
    anonymize()