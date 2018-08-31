""" verify_client_version Conftest
conftest to setup required fixtures needed by tests:
- config for multihost plugin
"""

import pytest
from ipa_pytests.qe_class import multihost
from ipa_pytests.qe_install import setup_master, uninstall_server


def pytest_namespace():
    """ Define the number of test host roles using namespace hook """
    return {'num_replicas': 0,
            'num_clients': 0,
            'num_masters': 1,
            'num_others': 0
            }


@pytest.fixture(scope="session", autouse=True)
def setup_session(request, multihost):
    try:
        setup_master(multihost.master)
    except Exception as errval:
        print(str(errval.args[0]))
        pytest.skip("setup_session_skip")

    def teardown_session():
        """ define fixture for session level teardown """
        uninstall_server(multihost.master)
    request.addfinalizer(teardown_session)
