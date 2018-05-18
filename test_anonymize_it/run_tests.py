import sys
import pytest


def run_all(argv=None):
    if argv is None:
        argv = ['--cov', 'anonymize_it', '--verbose', '--junitxml', 'junit.xml', '--cov-report', 'xml']
    else:
        argv = argv[1:]

    sys.exit(pytest.main(argv))

if __name__ == "__main__":
    run_all(sys.argv)