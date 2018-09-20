# pylint: disable=R0801
""" OTP Conftest
conftest to setup required fixtures needed by tests:
- config for multihost plugin
"""


import pytest
from ipa_pytests.qe_install import setup_master, setup_client
from ipa_pytests.shared.rpm_utils import check_rpm
from ipa_pytests.qe_class import multihost  # pylint: disable=unused-import
from ipa_pytests.qe_class import qe_use_class_setup # pylint: disable=unused-import

def pytest_namespace():
    """ Define the number of test host roles using namespace hook """
    return {'num_replicas': 0,
            'num_clients': 1,
            'num_others': 0}


@pytest.fixture(scope="session", autouse=True)
def setup_session(request, multihost):
    """ Setup session """
    multihost.password = "Secret123"
    multihost.secret = 'Secret123'
    try:
        multihost.client = multihost.clients[0]
        setup_master(multihost.master)
        setup_client(multihost.client, multihost.master)
        #multihost.master.yum_install(['expect'])

    except Exception as errval:
        print("Error in setup_session %s" % (str(errval.args[0])))
        pytest.skip("setup_session_skip")

    def teardown_session():
        """ define fixture for session level teardown """
        pass

    request.addfinalizer(teardown_session)
