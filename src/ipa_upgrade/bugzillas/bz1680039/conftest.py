""" Conftest for server install """
import pytest
from ipa_pytests.shared.yum_utils import add_repo
from ipa_pytests.qe_class import multihost
from ipa_pytests.ipa_upgrade.constants import repo_urls
from ipa_pytests.qe_install import setup_master, uninstall_server

def pytest_namespace():
    """ Define the number of test host roles using namespace hook """
    return {'num_replicas': 0,
            'num_clients': 0,
            'num_others': 0,
            'num_ads': 0
            }


@pytest.fixture(scope="session", autouse=True)
def setup_session(request, multihost):
    try:
        setup_master(multihost.master)
        print ("Setup done")

    except Exception as errval:
        print("Error in setup_session %s" % str(errval))
        pytest.fail("setup_session_fail")

    def teardown_session():
        """ define fixture for session level teardown """
        uninstall_server(multihost.master)
        print(" This is teardown session")

    request.addfinalizer(teardown_session)
