""" Functional Services Conftest
conftest to setup required fixtures needed by tests:
- config for multihost plugin
- setup session scoped setup and teardown
- must include import for multihost fixture if using multihost plugin
- must include import for qe_use_class_setup fixture if test class will have
  class_setup and class_teardown methods.
"""

import pytest
from ipa_pytests.qe_class import multihost  # pylint: disable=unused-import
from ipa_pytests.qe_class import qe_use_class_setup  # pylint: disable=unused-import
from ipa_pytests.functional_services import setup_lib
from ipa_pytests.qe_class import pytest_runtest_makereport


def pytest_namespace():
    """ Define the number of test host roles using namespace hook """
    return {'num_replicas': 1,
            'num_clients': 1,
            'num_others': 0,
            'num_ads': 0}


@pytest.fixture(scope="session", autouse=True)
def setup_session(request, multihost):
    """ define fixture for session level setup """
    # Defining convenience variables for multihost fixture
    # for single replica and client
    multihost.replica = multihost.replicas[0]
    multihost.client = multihost.clients[0]

    tp = setup_lib.TestPrep(multihost)
    try:
        tp.setup()
    except Exception as errval:
        print(str(errval.args[0]))
        pytest.exit(str(errval.args[0]))
        #pytest.skip("setup_session_skip")

    def teardown_session():
        """ define fixture for session level teardown """
        tp.teardown()
    request.addfinalizer(teardown_session)
