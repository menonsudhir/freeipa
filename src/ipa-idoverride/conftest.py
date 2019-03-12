""" verify_client_version Conftest
conftest to setup required fixtures needed by tests:
- config for multihost plugin
"""


import pytest
from ipa_pytests.qe_install import setup_client, setup_master
#from ipa_pytests.qe_class import multihost

def pytest_namespace():
    """ Define the number of test host roles using namespace hook """
    return {'num_replicas': 0,
            'num_clients': 0,
            'num_others': 0,
            'num_ads': 1
            }

