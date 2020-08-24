""" Conftest for upgrade """
import pytest
from ipa_pytests.qe_class import multihost
from ipa_pytests.qe_install import (setup_master,
                                    setup_replica)
from ipa_pytests.qe_install import uninstall_server


def pytest_namespace():
    """ Define the number of test host roles using namespace hook """
    return {'num_replicas': 1,
            'num_clients': 0,
            'num_others': 0,
            'num_ads': 0
            }


@pytest.fixture(scope="session", autouse=True)
def setup_session(request, multihost):
    multihost.replica = multihost.replicas[0]
    try:
        setup_master(multihost.master)
        setup_replica(multihost.replica, multihost.master)
        print("Setup done")

    except Exception as errval:
        print("Error in setup_session %s" % str(errval))
        pytest.fail("setup_session_fail")

    def teardown_session():
        """ define fixture for session level teardown """
        # uninstall_server(multihost.master)
        # uninstall_server(multihost.master)

    request.addfinalizer(teardown_session)

