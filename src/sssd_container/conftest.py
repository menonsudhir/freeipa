"""
Test cases for sssd-container with IPA.
"""
import pytest
from ipa_pytests.qe_class import multihost


def pytest_namespace():
    """ Define the number of test host roles using namespace hook """
    return {'num_replicas': 0,
            'num_clients': 1,
            'num_others': 0}


@pytest.fixture(scope="session", autouse=True)
def setup_session(request, multihost):
    multihost.client = multihost.clients[0]

    def teardown_session():
        """ define fixture for session level teardown """
        print('This is teardown session')
        contents = multihost.client.get_file_contents('/etc/resolv.conf.backup')
        multihost.client.put_file_contents('/etc/resolv.conf', contents)
    request.addfinalizer(teardown_session)
