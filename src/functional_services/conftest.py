# pylint: disable=R0801
""" Functional Services Conftest
conftest to setup required fixtures needed by tests:
- config for multihost plugin
- setup session scoped setup and teardown
"""

import pytest
from pytest_multihost import make_multihost_fixture
from ipa_pytests import qe_class
from ipa_pytests.shared.logger import log
from ipa_pytests.functional_services import setup_lib


@pytest.fixture(scope="session", autouse=True)
def multihost(request):
    """ Mulithost plugin fixture for session scope """
    print request.node
    mh = make_multihost_fixture(
        request,
        descriptions=[
            {
                'type': 'ipa',
                'hosts': {
                    'master': 1,
                    'replica': 1,
                    'client': 1,
                },
            },
        ],
        config_class=qe_class.QeConfig
    )
    mh.domain = mh.config.domains[0]
    [mh.master] = mh.domain.hosts_by_role('master')
    [mh.replica] = mh.domain.hosts_by_role('replica')
    [mh.client] = mh.domain.hosts_by_role('client')
    return mh


@pytest.fixture(scope='class', autouse=True)
def setup_class(request, multihost):
    """ define fixture to run class_setup and teardown"""
    if hasattr(request.cls(), 'class_setup'):
        try:
            request.cls().class_setup(multihost)
        except StandardError:
            pytest.skip("class_setup_failed")
        request.addfinalizer(lambda: request.cls().class_teardown(multihost))


@pytest.fixture(scope="session", autouse=True)
def setup_session(request, multihost):
    """ define fixture for session level setup """
    tp = setup_lib.TestPrep(multihost)
    try:
        tp.setup()
    except StandardError:
        pytest.skip("setup_session_skip")

    def teardown_session():
        """ define fixture for session level teardown """
        tp.teardown()
    request.addfinalizer(teardown_session)


@pytest.fixture(scope="function", autouse=True)
def mark_test_start(request):
    """ define fixture to log start of tests """
    logmsg = "MARK_TEST_START: " + request.function.__name__
    log.critical(logmsg)

    def mark_test_stop():
        """ define fixture to log end of tests """
        logmsg = "MARK_TEST_STOP: " + request.function.__name__
        log.critical(logmsg)
    request.addfinalizer(mark_test_stop)
