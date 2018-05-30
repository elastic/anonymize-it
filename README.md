# anonymize-it
a general utility for anonymizing data

`anonymize-it` can be run as a script that accepts a config file specifying the type source, anonymization mappings, and destination and an anonymizer pipeline. Individual pipeline components can also be imported into any python program that wishes to anonymize data. 

Currently, the anonymization procedue relies on providers from [`Faker`](http://faker.readthedocs.io) to perform masking of fields.

e.g.:

```
>>> from faker import Faker
>>> f = Faker()
>>> f.file_path()
'/break/Congress.json'
```


# Instructions for use

## Installation

This must be run in a virtualenvironment with the correct dependencies installed. These are enumerated in `requirements.txt`

### Install `virtualenv` globally:

```
[sudo] pip install virtualenv
```

Create a virtualenv and install the dependencies of `anonymize-it`
```
virtualenv -p python3 venv
source venv/bin/activate
pip install -r requirements.txt
```

and run:

```
python anonymize.py configs/config.json
```

## Quick Start
`anonymize.py` is reproduced below to walk through a simple anonymization pipeline.


First load and parse the config file.
 
```python
config_file = sys.argv[1]
config = read_config(config_file) # opens json file and stores as python dict
config = utils.parse_config(config) # utility function for parsing configuration and setting variables
```

Then, create the reader as defined in the configuration. `reader_mapping` is used as a dispatcher that maps human reader reader types (e.g. elasticsearch) to reader classes (e.g. `ESReader()`).
```python
reader = reader_mapping[config.source['type']]
reader = reader(config.source['params'], config.masked_fields, config.suppressed_fields)
```

Next, create the writer in the same way.
```python
writer = writer_mapping[config.dest['type']]
writer = writer(config.dest['params'])
```

Finally, create an anonymizer by passing the reader and writer instances and run `anonymize()`.
```python
anon = Anonymizer(reader=reader, writer=writer)
anon.anonymize()
```

### Creating your own anonymizer pipeline

An anonymizer requires a `reader` and a `writer`. Currently, only an elasticsearch reader `readers.ESReader()` and a filesystem writer `writers.FSWriter()` are provided.

#### `readers`
Creating an instance of a reader requires the following:

* a `source` object, which contains parameters about the source. Please note that each reader class requires a different set of parameters. Please consult docstrings for specific parameters. 
* `masked_fields` which is a dictionary that contains field names that should be masked, along with the faker provider to be used for masking. e.g.: `{"user.name": "user_name", "user.email": "email"}`
* `suppressed_fields` which is a list of fields that should not be included in anonymization.

`masked_fields` is required on the reader since the reader is responsible for enumerating the distinct values for each field to be used as a lookup for masking values.

`suppressed_fields` is required on the reader since we will explicitly exclude these from a search query.

Readers must implement the following methods:

* `create_mappings()`, which is responsible for generating a dictionary to be used by the anonymizer object. The dictionary is structured as so:
    ```python
    {
      "field.1": {
          "val1.1": None,
          "val1.2": None,
          ...,
          "val1.n": None
        },
      "field.2": {
          "val2.1": None,
          "val2.2": None,
          ...,
          "val2.m": None
        }
    }
    ``` 
* `get_data()`, which is responsible for returning data from the source and passing it to the anonymizer.

#### `writers`

Creating an instance of a writer requires the following:

*  A `dest` object, which contains parameters about the destination. Please note that each writer class requires a different set of parameters. Please consult docstrings for specific parameters.

Writers must implement the following methods:

* `write_data()`, which send anonymized data to the destination.

## Run as Script


#### `anonymizers`

```
python anonymize.py configs/config.json
```


`config.json` defines the work to be done, please see template file at `configs/config.json` for guidance:

*  `source` defines the location of the original data to be anonymized along with the type of reader that should be invoked.
   *  `source.type`: a reader type. one of:
      * "elasticsearch"
      * "csv" (TBD)
      * "json" (TBD)
   * `source.params`: parameters allowing for access of data. specific to the reader type.
      * "elasticsearch":
         * `host`
         * `username`
         * `password`
         * `index`
* `dest` defines the location where the data should be written back to
    * `dest.type` a writer type. one of:
        * "filesystem"
        * "csv' (TBD)
        * "elasticsearch" (TBD)
    * `dest.params`: parameters allowing for writing of data. specific to writer types
       * "json":
          * `directory` : directory to write json files
* `include`: the fields to mask along with the method for anonymization. This is a dict with entries like `{"field.name":"faker.provider.mask"}`. Please see faker documentation for providers [here](http://faker.readthedocs.io/en/master/providers.html).
* `exclude`: specific fields to exclude
* `include_rest`: `{true|false}` if true, all fields except excluded fields will be written. if false, only fields specified in `masks` will be written.

## Use Classes

To be added.

# Adding Masks

The anonymizer class only knows how to use providers that are enumerated in the `provider_map` class attribute. If you would like to add support for new faker providers, please add entries to this dict.

# Adding Readers

Readers can be added to `readers.py`, simply extend the base reader class and implement all abstract methods. Add a new entry to `mappings`

# Adding Writers

Readers can be added to `writers.py`, simply extend the base writer class and implement all abstract methods. Add a new entry to `mappings` 

# Notes

https://stackoverflow.com/questions/17486578/how-can-you-bundle-all-your-python-code-into-a-single-zip-file