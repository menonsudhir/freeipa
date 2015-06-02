# pylint: disable=R0801
""" Functional Services Conftest
conftest to setup required fixtures needed by tests:
- config for multihost plugin
- setup session scoped setup and teardown
"""

import pytest
from pytest_multihost import make_multihost_fixture
from ipa_pytests import qe_class
from ipa_pytests.functional_services.setup_lib import setup_ipa_env
from ipa_pytests.functional_services.setup_lib import setup_http_service
from ipa_pytests.functional_services.setup_lib import setup_ldap_service


@pytest.fixture(scope="session")
def session_multihost(request):
    """ Mulithost plugin fixture for session scope """
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


@pytest.fixture(scope='class')
def multihost(session_multihost, request):
    """ multihost plugin fixture for class scope """
    if hasattr(request.cls(), 'class_setup'):
        request.cls().class_setup(session_multihost)
        request.addfinalizer(lambda: request.cls().class_teardown(session_multihost))
    return session_multihost


@pytest.fixture(scope="session", autouse=True)
def setup_session(request, session_multihost):
    """ define fixture for session level setup """
    tp = TestPrep(session_multihost)
    tp.setup()

    def teardown_session():
        """ define fixture for session level teardown """
        tp.teardown()
    request.addfinalizer(teardown_session)


class TestPrep(object):
    """ Session level setup/teardown class """
    def __init__(self, multihost):

        self.multihost = multihost

    def setup(self):
        """
        Session level setup.
        - Add code here that you want run before all modules in test suite.
        - This should be teardown/cleanup code only, not test code.
        """

        fin = '/tmp/ipa_func_svcs_setup_done'
        if not self.multihost.client.transport.file_exists(fin):
            setup_ipa_env(self.multihost)
            setup_http_service(self.multihost)
            setup_ldap_service(self.multihost)
            self.multihost.client.put_file_contents(fin, 'x')
        else:
            print "Setup has already run.  Skipping"

    def teardown(self):
        """
        Session level teardown
        - Add code here that you want run after all modules in test suite.
        - This should be teardown/cleanup code only, not test code.
        """
        pass
