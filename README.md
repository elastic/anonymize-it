# anonymize-it
A general utility for anonymizing data

`anonymize-it` can be run as a script that accepts a config file specifying the type source, anonymization mappings, and destination and an anonymizer pipeline. Individual pipeline components can also be imported into any python program that wishes to anonymize data. 

Currently, the `anonymize-it` supports two methods for anonymization: 
1) Faker-based: Relies on providers from [`Faker`](http://faker.readthedocs.io) to perform masking of fields. This method is suitable for one-off anonymization usecases, where correlation between data obtained from different sources (indices/clusters) is not necessary.

E.g.:

```
>>> from faker import Faker
>>> f = Faker()
>>> f.file_path()
'/break/Congress.json'
```
2) Hash-based: Uses a unique user/customer ID as a salt to anonymize fields. This method is suitable when anonymization of data needs to be performed regularly and/or if correlation of data from different sources is crucial. 

E.g.: A user wants to anonymize network events and process events stored in two separate indices but wants to correlate all activity for a particular host even after anonymization

# Disclaimer

`anonymize-it` is intended to serve as a tool to replace real data values with sensical artificial ones such that the semantics of the data are retained. It is not intended to be used for anonymization requirements of GDPR policies, but rather to aid pseudonymization efforts. There may also be some collisions in high cardinality datasets on using the Faker implementation.

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
* `masked_fields` which is a dictionary that contains field names that should be masked, along with the faker provider to be used for masking, if using the Faker-base anonymization. e.g.: `{"user.name": "user_name", "user.email": "email"}`
If using the hash-based implementation, `masked_fields` is simply a list of field names to be masked. e.g.: `["user.name", "user.email"]`
* `suppressed_fields` which is a list of fields that should NOT be included in anonymization.

`masked_fields` is required on the reader since the reader is responsible for enumerating the distinct values for each field to be used as a lookup for masking values in the faker-based anonymization.

`suppressed_fields` is required on the reader since we will explicitly exclude these from a search query.

Readers must implement the following methods:
* `get_data()`, which is responsible for returning data from the source and passing it to the anonymizer.
* (If using Faker-based anonymization), `create_mappings()`, which is responsible for generating a dictionary to be used by the anonymizer object. The dictionary is structured as so:
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
where `field.1` and `field.2` are the fields to be anonymized and the `val1.1`, `val1.2` etc. are the distinct values for each field

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
         * `index`
         * `use_ssl`
         * `auth` (`native` optional)
* `dest` defines the location where the data should be written back to
    * `dest.type` a writer type. one of:
        * "filesystem"
        * "csv' (TBD)
        * "elasticsearch" (TBD)
    * `dest.params`: parameters allowing for writing of data. specific to writer types
       * "json":
          * `directory` : directory to write output json files
* `anonymization`: type of anonymization i.e. `faker` or `hash`
* `include`: the fields to mask along with the method for anonymization in case of faker-based anonymization. This is a dict with entries like `{"field.name":"faker.provider.mask"}`. Please see faker documentation for providers [here](http://faker.readthedocs.io/en/master/providers.html).
For hash-based anonymization, this can be a list of fields to be masked like `["field.name"]`.
* `exclude`: specific fields to exclude
* `sensitive`: included fields (apart from the masked fields) that should be searched for sensitive information like secrets
* `include_rest`: `{true|false}` if true, all fields except excluded fields will be written. if false, only fields specified in `masks` will be written.

#### Important notes for hash-based anonymization
1) The user should have `monitor` privilege for the Elastic environment in which to run the anonymization.
2) If you are a Cloud user and want to perform hash-based anonymization, you'll need to create an API key in the Elasticsearch Service Console and provide it as input when prompted. To create an API key, follow the instructions [here](https://www.elastic.co/guide/en/cloud/current/ec-api-authentication.html).

# Adding Masks

For the faker-based anonymization, the anonymizer class only knows how to use providers that are enumerated in the `provider_map` class attribute. If you would like to add support for new faker providers, please add entries to this dict.

# Adding Readers

Readers can be added to `readers.py`, simply extend the base reader class and implement all abstract methods. Add a new entry to `reader_mapping`

# Adding Writers

Readers can be added to `writers.py`, simply extend the base writer class and implement all abstract methods. Add a new entry to `reader_mapping` 

# General Notes
https://stackoverflow.com/questions/17486578/how-can-you-bundle-all-your-python-code-into-a-single-zip-file

# Running Tests

To run the unit tests, 
1. Create a virtual environment and install dependencies in `requirements.txt`
2. Execute `py.test` from the top-level repository directory
