""" Multihomed conftest
- config for multihost plugin
"""

import pytest
from ipa_pytests.qe_class import multihost
from ipa_pytests.qe_class import qe_use_class_setup


def pytest_namespace():
    """ Define the number of test host roles using namespace hook """
    return {'num_replicas': 1,
            'num_clients': 1,
            'num_others': 0}


@pytest.fixture(scope="session", autouse=True)
def setup_session(request, multihost):
    """ define fixture for session level setup """
    multihost.replica = multihost.replicas[0]
    multihost.client = multihost.clients[0]
