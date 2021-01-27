- Values to be set in anonymizers.py
- provider_map and high_cardinality_fields need to be set only if anonymization_type=faker

provider_map = {<br/>
    "host.hostname": self.faker.word,<br/>
    "host.ip": self.faker.ipv4,<br/>
    "labels.account_id": self.faker.ssn,<br/>
    "labels.endpoint_id": self.faker.ssn,<br/>
    "observer.name": self.faker.word,<br/>
    "user.domain": self.faker.word,<br/>
    "user.name": self.faker.word<br/>
}

high_cardinality_fields = {}

user_regexes = {<br/>
    "user_dir_1": "(Users)\\\\([^\\\\]+)",<br/>
    "user_dir_2": "(Users)\\/([^\\/]+)"<br/>
}

keywords = [<br/>
    "wget",<br/>
    "ssh",<br/>
    "aws",<br/>
    "curl"<br/>
]
