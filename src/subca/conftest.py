# pylint: disable=R0801
""" IPA Lightweight Sub CA Conftest
conftest to setup required fixtures needed by tests:
- config for multihost plugin
"""

import pytest
from ipa_pytests.qe_install import setup_replica, setup_master
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
    # for single replica and client
    multihost.replica = multihost.replicas[0]
    passwd = multihost.master.config.admin_pw
    for host in [multihost.master, multihost.replica]:
        host.yum_install(['expect'])
    try:
        setup_master(multihost.master)
        setup_replica(multihost.replica, multihost.master)
        multihost.replica.kinit_as_admin()
        cmd = 'ipa-ca-install -p {0} -w {1}'.format(passwd, passwd)
        multihost.replica.run_command(cmd, raiseonerr=False)
    except Exception as errval:
        print("Error in setup_session %s" % (str(errval.args[0])))
        pytest.skip("setup_session_skip")

    def teardown_session():
        """ define fixture for session level teardown """
        print("Teardown Session for Sub CA")
    request.addfinalizer(teardown_session)
