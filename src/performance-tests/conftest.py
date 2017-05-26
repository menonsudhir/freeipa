import pytest
import os
from ipa_pytests.qe_install import setup_master, setup_replica, uninstall_server
from ipa_pytests.qe_class import multihost
from ipa_pytests.qe_class import qe_use_class_setup
from ipa_pytests.shared.utils import service_control

def pytest_namespace():
    """ Define the number of test host roles using namespace hook.
        Here using variable resource_count to accept input values
        from CI job. """
    #resource_count = os.getenv("RESOURCE_COUNT", 5)
    resource_count=6
    replica_count = (int(resource_count) - 1)
    return {'num_replicas': replica_count,
            'num_clients': 0,
            'num_others': 0,
            'num_ads': 0}


@pytest.fixture(scope="session", autouse=True)
def setup_session(request, multihost):
    try:
        setup_master(multihost.master)

    except StandardError as errval:
        print("Error in setup_session %s" % (str(errval.args[0])))
        pytest.skip("setup_session_skip")

    def teardown_session():
        """ define fixture for session level teardown """
        uninstall_server(multihost.master)

    request.addfinalizer(teardown_session)
