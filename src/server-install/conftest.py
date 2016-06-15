""" Conftest for server install """
import pytest
from ipa_pytests.qe_install import setup_master, uninstall_server


def pytest_namespace():
    """ Define the number of test host roles using namespace hook """
    return {'num_replicas': 1,
            'num_clients': 0,
            'num_others': 1,
            'num_ads': 0
            }


@pytest.fixture(scope="session", autouse=True)
def setup_session(request, multihost):
    """ Setup Master"""
    setup_master(multihost.master)

    def teardown_session():
        """ define fixture for session level teardown """
        """ This is teardown session"""
        uninstall_server(multihost.master)
    request.addfinalizer(teardown_session)
