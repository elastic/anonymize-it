# anonymize-it
a general utility for anonymizing data

# Instructions for use

`config.json` defines the work to be done:

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
        * "json"
        * "csv' (TBD)
        * "elasticsearch" (TBD)
    * `dest.params`: parameters allowing for writing of data. specific to writer types
       * "json":
          * `directory` : directory to write json files
          * `lines`: `{true|false}` type of json to write
          * `chunked`: `{true|false}` one big file or many files
* `masks`: the fields to mask along with the method for anonymization. This is a dict with entries like `{"field.name":"faker.provider.mask"}`. Please see faker documentation for providers [here](http://faker.readthedocs.io/en/master/providers.html).
* `exclude`: specific fields to exclude
* `include_rest`: `{true|false}` if true, all fields except excluded fields will be written. if false, only fields specified in `masks` will be written.

e.g.:

```json
{
  "source": {
    "type": "elasticsearch",
    "params": {
      "host": "https://egergiuhewrgoiwehjgr239024t.us-west-1.aws.found.io:9243/",
      "username": "elastic",
      "password": "changeme",
      "index": "apm-*"
    }
  },
  "dest":{
    "type": "filesystem",
    "params": {
      "directory": "blaklaybul/anonymized/output/",
      "lines": false,
      "chunked": false
    }
  },
  "masks": {
    "context.request.url" : "url",
    "docker.container.id": "ipv4"
  },
  "exclude": ["user.name"],
  "include_all": false
}
```

# Adding Masks

The anonymizer class only knows how to use providers that are enumerated in the `provider_map` class attribute. If you would like to add support for new faker providers, please add entries to this dict.

# Adding Readers

Readers can be added to `readers.py`, simply extend the base reader class and implement all abstract methods. Add a new entry to `mappings`

# Adding Writers

Readers can be added to `writers.py`, simply extend the base writer class and implement all abstract methods. Add a new entry to `mappings` 