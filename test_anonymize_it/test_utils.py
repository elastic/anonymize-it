from anonymize_it import utils


def test_flatten_nest():
    old = {
        "this": {
            "is": {
                "a": {
                    "test": True
                }
            }
        }
    }

    flattened = utils.flatten_nest(old)
    new = {"this.is.a.test": True}
    assert new == flattened
