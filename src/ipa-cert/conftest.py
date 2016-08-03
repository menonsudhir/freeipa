""" certificate signing request - Conftest
conftest to setup required fixtures needed by tests:
- config for multihost plugin
"""

import pytest
from ipa_pytests.qe_install import setup_master, uninstall_server


@pytest.fixture(scope="session", autouse=True)
def setup_session(request, multihost):
    """ Setup session """
    try:
        setup_master(multihost.master)
        print ("Setup done")

    except StandardError as errval:
        print("Error in setup_session %s" % (str(errval.args[0])))
        pytest.skip("setup_session_skip")

    def teardown_session():
        """ define fixture for session level teardown """
        uninstall_server(multihost.master)

    request.addfinalizer(teardown_session)
