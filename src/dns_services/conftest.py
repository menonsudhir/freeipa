'''Automation of RFE for BZ#1207539 BZ#1211608 BZ#1207541.'''
import pytest
from ipa_pytests.qe_install import setup_master
from ipa_pytests.qe_install import uninstall_server
from ipa_pytests.qe_class import multihost


def pytest_namespace():
    """ Define the number of test host roles using namespace hook """
    return {'num_replicas': 0,
            'num_clients': 0,
            'num_others': 0}


@pytest.fixture(scope="session", autouse=True)
def setup_session(request, multihost):
    '''Setup master'''
    setup_master(multihost.master)

    def teardown_session():
        """ define fixture for session level teardown """
        print('This is teardown session, uninstalling server')
        uninstall_server(multihost.master)
    request.addfinalizer(teardown_session)
