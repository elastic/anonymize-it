* Values to be set in anonymizers.py
* provider_map and high_cardinality_fields need to be set only if anonymization_type=faker

```python
    {
      "provider_map": {
          "host.hostname": self.faker.word,
          "host.ip": self.faker.ipv4,
          "labels.account_id": self.faker.ssn,
          "labels.endpoint_id": self.faker.ssn,
          "observer.name": self.faker.word,
          "user.domain": self.faker.word,
          "user.name": self.faker.word,
          "user.effective.name": self.faker.word,
          "user.effective.domain": self.faker.word
        },
      "high_cardinality_fields": {},
      "user_regexes": {
          "user_dir_1": "(Users)\\\\([^\\\\]+)",
          "user_dir_2": "(Users)\\/([^\\/]+)"
        },
      "keywords": [
          "wget",
          "ssh",
          "aws",
          "curl"
        ]
    }
``` 
