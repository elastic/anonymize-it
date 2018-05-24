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

## Run as Script

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
