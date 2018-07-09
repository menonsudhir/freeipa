""" Conftest for server install """
import pytest
from ipa_pytests.qe_class import multihost
from ipa_pytests.qe_class import qe_use_class_setup


def pytest_namespace():
    """ Define the number of test host roles using namespace hook """
    return {'num_replicas': 0,
            'num_clients': 0,
            'num_others': 0,
            'num_ads': 0
            }


@pytest.fixture(scope="session", autouse=True)
def setup_session(request, multihost):

    def teardown_session():
        """ define fixture for session level teardown """
        """ This is teardown session"""

    request.addfinalizer(teardown_session)



