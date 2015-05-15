import os
import coverage

os.environ['COVERAGE_PROCESS_START']= "/root/multihost_tests/.coveragerc"
os.environ['COVERAGE_FILE'] = "/root/multihost_tests/ipa-pytests-coverage-data"
coverage.process_startup()
