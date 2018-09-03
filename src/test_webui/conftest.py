# pylint: disable=R0801
""" test_webui Conftest
conftest to setup required fixtures needed by tests:
- config for multihost plugin
"""

import pytest
from ipa_pytests.qe_install import setup_master
from ipa_pytests.qe_class import multihost
from ipa_pytests.qe_class import qe_extra_print
from ipa_pytests.qe_class import qe_use_class_setup
from ipa_pytests.test_webui import ui_lib


def pytest_namespace():
    """ Define the number of test host roles using namespace hook """
    return {'num_replicas': 0,
            'num_clients': 0,
            'num_others': 0
            }


@pytest.fixture(scope="session", autouse=True)
def setup_session(request, multihost):
    """ Setup session with ui_lib and master setup"""
    tp = ui_lib.ui_driver(multihost)
    try:
        tp.setup()
        setup_master(multihost.master)
        multihost.driver = tp
    except Exception as errval:
        pytest.skip("setup_session_skip : %s" % (errval.args[0]))

    def teardown_session():
        """ define fixture for session level teardown """
        tp.teardown()
    request.addfinalizer(teardown_session)
