# pylint: disable=R0801
""" Certificate profile conftest
conftest to setup required fixtures needed by tests:
- config for multihost plugin
"""

import pytest
from ipa_pytests.qe_class import multihost
from ipa_pytests.qe_install import (setup_client, setup_master, setup_replica,
                                    uninstall_server)


def pytest_namespace():
    """ Define the number of test host roles using namespace hook """
    return {'num_replicas': 1,
            'num_clients': 0,
            'num_others': 0,
            'num_ads': 0}


@pytest.fixture(scope="session", autouse=True)
def setup_session(request, multihost):
    """ Setup session """
    try:
        setup_master(multihost.master)
        setup_replica(multihost.replicas[0], multihost.master)
    except Exception as errval:
        print("\nError in setup_session %s" % (str(errval.args[0])))
        pytest.skip("setup_session_skip")

    def teardown_session():
        """ define fixture for session level teardown """
        uninstall_server(multihost.master)
        uninstall_server(multihost.replicas[0])
    request.addfinalizer(teardown_session)
