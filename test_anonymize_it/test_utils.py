from anonymize_it import utils


def test_flatten():
    old = {
        "this": {
            "is": {
                "a": {
                    "test": True
                }
            }
        }
    }

    flattened = utils.flatten(old)
    new = {"this.is.a.test": True}
    assert new == flattened