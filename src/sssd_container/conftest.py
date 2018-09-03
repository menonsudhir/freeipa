import pytest
from ipa_pytests.qe_install import setup_master_docker, uninstall_master_docker
from ipa_pytests.qe_class import multihost


def pytest_namespace():
    """ Define the number of test host roles using namespace hook """
    return {'num_replicas': 0,
            'num_clients': 1,
            'num_others': 0,
            'num_ads': 0}


@pytest.fixture(scope="session", autouse=True)
def setup_session(request, multihost):
    try:
        setup_master_docker(multihost.master)
        print("setup_master_docker")
        multihost.client = multihost.clients[0]


    except Exception as errval:
        print("Error in setup_session %s" % (str(errval.args[0])))
        pytest.skip("setup_session_skip")

    def teardown_session():
        """ define fixture for session level teardown """
        print("This is teardown")
        uninstall_master_docker(multihost.master)
    request.addfinalizer(teardown_session)
