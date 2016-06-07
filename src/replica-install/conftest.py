""" Conftest for replica install """
import pytest


def pytest_namespace():
    """ Define the number of test host roles using namespace hook """
    return {'num_replicas': 1,
            'num_clients': 0,
            'num_others': 0
            }


@pytest.fixture(scope="session", autouse=True)
def setup_session(request, multihost):
    multihost.replica = multihost.replicas[0]

    def teardown_session():
        """ define fixture for session level teardown """
        pass
    request.addfinalizer(teardown_session)
