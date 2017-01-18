""" Functional Services Conftest
conftest to setup required fixtures needed by tests:
- config for multihost plugin
- setup session scoped setup and teardown
- must include import for multihost fixture if using multihost plugin
- must include import for qe_use_class_setup fixture if test class will have
  class_setup and class_teardown methods.
"""

import pytest
from ipa_pytests.qe_class import multihost
from ipa_pytests.qe_class import qe_use_class_setup
from ipa_pytests.qe_install import setup_master, setup_client


def pytest_namespace():
    """ Define the number of test host roles using namespace hook """
    return {'num_replicas': 0,
            'num_clients': 1,
            'num_ads': 1,
            'num_others': 0}


@pytest.fixture(scope="session", autouse=True)
def setup_session(request, multihost):
    """ define fixture for session level setup """
    # Defining convenience variables for multihost fixture
    # for single master and client
    multihost.client = multihost.clients[0]
    multihost.realm = multihost.master.domain.realm

    setup_master(multihost.master)
    multihost.master.yum_install(['expect'])
    setup_client(multihost.client, multihost.master)
    multihost.client.yum_install(['expect'])

    def teardown_session():
        """ define fixture for session level teardown """
        pass

    request.addfinalizer(teardown_session)
