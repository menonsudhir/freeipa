# pylint: disable=R0801
""" IPA Replica Promotion Conftest
conftest to setup required fixtures needed by tests:
- config for multihost plugin
"""

import pytest
from ipa_pytests.qe_install import setup_master, uninstall_server
from ipa_pytests.qe_class import multihost
from ipa_pytests.qe_class import qe_use_class_setup


def pytest_namespace():
    """ Define the number of test host roles using namespace hook """
    return {'num_replicas': 1,
            'num_clients': 0,
            'num_others': 0,
            'num_ads': 0}


@pytest.fixture(scope="session", autouse=True)
def setup_session(request, multihost):
    """ Setup session """
    # Defining convenience variables for multihost fixture
    # for single replica
    multihost.replica = multihost.replicas[0]
    try:
        setup_master(multihost.master, setup_kra=True)
    except StandardError as errval:
        print("Error in setup_session %s" % (str(errval.args[0])))
        pytest.skip("setup_session_skip")

    def teardown_session():
        """ define fixture for session level teardown """
        uninstall_server(multihost.master)
    request.addfinalizer(teardown_session)
