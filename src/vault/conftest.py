# pylint: disable=R0801
""" Functional Services Conftest
conftest to setup required fixtures needed by tests:
- config for multihost plugin
- setup session scoped setup and teardown
"""

import pytest
from ipa_pytests.qe_class import multihost  # pylint: disable=unused-import
from ipa_pytests.qe_class import test_count  # pylint: disable=unused-import
from ipa_pytests.qe_class import mark_test_start  # pylint: disable=unused-import
from ipa_pytests.qe_class import qe_use_class_setup  # pylint: disable=unused-import
from ipa_pytests.shared.utils import add_ipa_user
from .lib import delete_all_vaults
from .lib import delete_all_vault_containers
import data  # pylint: disable=relative-import

# Leaving this import commented until we resolve xml formatting
# from ipa_pytests.qe_class import pytest_runtest_makereport


def pytest_namespace():
    """
    Pytest namespace global variables.  Must define the following:
    - num_replicas - number of replica hosts for the test
    - num_clients - number of client hosts for the test
    - num_others - number of other hosts for the test
    - count - start of count for test_count
    """
    return {'num_replicas': 1,
            'num_clients': 0,
            'num_others': 0,
            'count': 0}


@pytest.fixture(scope="function", autouse=True)
def make_vault_name(request):
    """
    make_vault_name fixture
    - provides a global VAULT_NAME variable based on test count number
      in the pytest.count global var we create from pytest_namespace
      above.
    """
    request.function.func_globals['VAULT_NAME'] = "idmqe_vault_%s" % pytest.count  # pylint: disable=E1101


@pytest.fixture(scope="session", autouse=True)
def setup_session(request, multihost):  # pylint: disable=W0621
    """ define fixture for session level setup """
    print "\nSETUP_SESSION RUNNING....\n"
    multihost.replica = multihost.replicas[0]
    data.init(multihost, 'test')
    add_ipa_user(multihost.master, data.USER1, data.PASSWORD)
    multihost.master.qerun(['ipa', 'service-add', data.SERVICE1 + "/" + multihost.master.hostname])

    if not multihost.master.transport.file_exists(data.PRVKEY_FILE):
        multihost.master.qerun(['openssl', 'genrsa', '-out', data.PRVKEY_FILE, '2048'])
    if not multihost.master.transport.file_exists(data.PUBKEY_FILE):
        multihost.master.qerun(['openssl', 'rsa', '-in', data.PRVKEY_FILE, '-out', data.PUBKEY_FILE,
                                '-pubout'])

    if not multihost.master.transport.file_exists(data.NEW_PRVKEY_FILE):
        multihost.master.qerun(['openssl', 'genrsa', '-out', data.NEW_PRVKEY_FILE, '2048'])
    if not multihost.master.transport.file_exists(data.NEW_PUBKEY_FILE):
        multihost.master.qerun(['openssl', 'rsa', '-in', data.NEW_PRVKEY_FILE, '-out',
                                data.NEW_PUBKEY_FILE, '-pubout'])

    if not multihost.master.transport.file_exists(data.PASS_FILE):
        multihost.master.transport.put_file_contents(data.PASS_FILE, data.PASSWORD)
    if not multihost.master.transport.file_exists(data.SECRET_FILE):
        multihost.master.transport.put_file_contents(data.SECRET_FILE, data.SECRET_VALUE)
    if not multihost.master.transport.file_exists(data.LARGE_FILE):
        multihost.master.qerun(['dd', 'if=/dev/zero', 'of=' + data.LARGE_FILE, 'bs=1024',
                                'count=4096'])
    if multihost.master.transport.file_exists(data.DNE_FILE):
        multihost.master.qerun(['rm', '-f', data.DNE_FILE])

    try:
        multihost.master.run_command(['ipa-kra-install', '-U',
                                      '-p', multihost.master.config.dirman_pw], raiseonerror=False)
    except StandardError:
        print "IPA KRA Install Failed"

    def teardown_session():
        """ define fixture for session level teardown """
        print "\nTEARDOWN_SESSION RUNNING...\n"
        delete_all_vaults(multihost.master)
        delete_all_vault_containers(multihost.master)
        multihost.master.qerun(['ipa', 'user-del', data.USER1])
        multihost.master.qerun(['ipa', 'service-del', data.SERVICE1 + "/" + multihost.master.hostname])
        # if multihost.master.transport.file_exists(data.PRVKEY_FILE):
        #     multihost.master.qerun(['rm', '-f', data.PRVKEY_FILE])
        # if not multihost.master.transport.file_exists(data.PUBKEY_FILE):
        #     multihost.master.qerun(['rm', '-f', data.PRVKEY_FILE])
    request.addfinalizer(teardown_session)
