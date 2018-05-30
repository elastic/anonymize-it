# Quickstart Guide

## Setup

Download `anonymize-it.zip` to a directory of your choice.

Create a configuration with the following structure:

```json
{
  "source": {
    "type": "elasticsearch",
    "params": {
      "host": "host:port",
      "index": "you-index-pattern-*",
      "query": {
        "match": {
          "username": "blaklaybul"
        }
      }
    }
  },
  "dest":{
    "type": "filesystem",
    "params": {
      "directory": "output"
    }
  },
  "include": {
    "field.1" : "file_path",
    "field.2": "ipv4",
    "@timestamp": null
  },
  "exclude": [],
  "include_rest": false
}
```

Make sure to update this configuration template for your data:
* change `source.params` to point to your elasticsearch cluster and the appropriate index or index pattern. You may also include a query.
* change `destination.params.directory` to a directory on your machine where you would like the output to be written. Output will be written as flattened json documents, each with 10,000 documents. Currently, files have auto-generated names in the form of `uuid4`.
* change `include` to the fields you would like to include in your output. If you would like to anonymize these fields, please type the faker provider you would like to use for anonymization (see providers here - [Faker docs](https://faker.readthedocs.io/en/master/providers.html)). If the field does not need to be anonymized, write `null`.
* `exclude` should be a list of fields that you would like to explicity exclude from search queries and output.
* `include_rest` if `true`, then all fields will be returned except those in exclude. If `false`, then only fields marked in `include` will be returned.   

Currently, `anonymize-it` only works with elasticsearch clusters as a source, and the local filesystem as a destination.

## Running

When your configuration is ready, `cd` to the directory where `anonymize-it.zip` is located. Then run:

```
PYTHONPATH=anonymize-it.zip python anonymize.py path/to/config
```

json files with anonymized data will be created in the directory specified by `dest.params.directory`.