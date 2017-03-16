""" UPN Conftest
conftest to setup required fixtures needed by tests:
- config for multihost plugin
- setup session scoped setup and teardown
- must include import for multihost fixture if using multihost plugin
- must include import for qe_use_class_setup fixture if test class will have
  class_setup and class_teardown methods.
"""

import pytest
from ipa_pytests.qe_class import multihost
from ipa_pytests.qe_install import setup_master
from ipa_pytests.qe_class import pytest_runtest_makereport


def pytest_namespace():
    """ Define the number of test host roles using namespace hook """
    return {'num_replicas': 0,
            'num_clients': 0,
            'num_ads': 1,
            'num_others': 0}


@pytest.fixture(scope="session", autouse=True)
def setup_session(request, multihost):
    """ define fixture for session level setup """
    # Defining convenience variables for multihost fixture
    # for single replica and client
    setup_master(multihost.master)

    def teardown_session():
        """ define fixture for session level teardown """
        pass
    request.addfinalizer(teardown_session)
