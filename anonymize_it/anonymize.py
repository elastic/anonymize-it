import sys
import json
from anonymizers import Anonymizer
from readers import reader_mapping
from writers import writer_mapping
import utils
import logging
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def read_config(config_file):
    with open(config_file, 'r') as f:
        config = json.load(f)
    return config


if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p ->', level=logging.INFO)

    logging.info("reading and parsing config file...")
    config_file = sys.argv[1]
    config = read_config(config_file)
    config = utils.parse_config(config)

    for conf in config._fields:
        logging.info("{} = {}".format(conf, getattr(config, conf)))

    logging.info("configuring reader...")
    reader = reader_mapping[config.source['type']]
    reader = reader(config.source['params'], config.masked_fields, config.suppressed_fields)

    logging.info("configuring writer...")
    writer = writer_mapping[config.dest['type']]
    writer = writer(config.dest['params'])

    logging.info("configuring anonymizer...")
    anon = Anonymizer(reader=reader, writer=writer)

    logging.info("performing anonymization...")
    anon.anonymize(infer=True)
