"""
Test cases for Bugzillas.
"""
import pytest
from ipa_pytests.qe_install import setup_master, uninstall_server, uninstall_client
from ipa_pytests.qe_class import multihost

def pytest_namespace():
    """ Define the number of test host roles using namespace hook """
    return {'num_replicas': 0,
            'num_clients': 1,
            'num_others': 0
            }


@pytest.fixture(scope="session", autouse=True)
def setup_session(request, multihost):
    setup_master(multihost.master)
    multihost.client = multihost.clients[0]

    def teardown_session():
        """ define fixture for session level teardown """
        print('This is teardown session, uninstalling client and server')
        uninstall_client(multihost.client)
        uninstall_server(multihost.master)
    request.addfinalizer(teardown_session)
