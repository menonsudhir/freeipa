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
from ipa_pytests.shared.user_utils import add_ipa_user  # pylint: disable=unused-import
from ipa_pytests.shared.user_utils import del_ipa_user  # pylint: disable=unused-import
from ipa_pytests.shared.keys import openssl_genrsa
from .lib import delete_all_vaults
from .lib import delete_all_vault_containers
from .lib import safe_setup_master
from .lib import safe_setup_replica
from .lib import safe_setup_master_kra
from . import data  # pylint: disable=relative-import

from ipa_pytests.qe_class import pytest_runtest_makereport


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
    request.function.__globals__['VAULT_NAME'] = "idmqe_vault_%s" % pytest.count  # pylint: disable=E1101


@pytest.fixture(scope="session", autouse=True)
def setup_session(request, multihost):  # pylint: disable=W0621
    """ define fixture for session level setup """
    print("\nSETUP_SESSION RUNNING....\n")
    multihost.replica = multihost.replicas[0]

    safe_setup_master(multihost.master)
    safe_setup_replica(multihost.replica, multihost.master)
    safe_setup_master_kra(multihost.master)

    multihost.master.yum_install(['expect'])
    multihost.replica.yum_install(['expect'])

    data.init(multihost, 'test')

    chk = multihost.master.run_command(['ipa', 'user-show', data.USER1],
                                       raiseonerr=False)
    if chk.returncode != 0:
        add_ipa_user(multihost.master, data.USER1, data.PASSWORD)

    chk = multihost.master.run_command(['ipa', 'service-show', data.SERVICE1],
                                       raiseonerr=False)
    if chk.returncode != 0:
        print("Adding service...{}".format(chk.returncode))
        multihost.master.qerun(['ipa', 'service-add', data.SERVICE1])

    openssl_genrsa(multihost.master, data.PRVKEY_FILE, data.PUBKEY_FILE)
    openssl_genrsa(multihost.master, data.NEW_PRVKEY_FILE, data.NEW_PUBKEY_FILE)
    multihost.master.transport.put_file_contents(data.PASS_FILE, data.PASSWORD)
    multihost.master.transport.put_file_contents(data.SECRET_FILE, data.SECRET_VALUE)
    multihost.master.qerun(['dd', 'if=/dev/zero', 'of=' + data.LARGE_FILE, 'bs=1024',
                            'count=4096'])
    multihost.master.qerun(['rm', '-f', data.DNE_FILE])

    def teardown_session():
        """ define fixture for session level teardown """
        print("\nTEARDOWN_SESSION RUNNING...\n")
        delete_all_vaults(multihost.master)
        delete_all_vault_containers(multihost.master)
        multihost.master.qerun(['ipa', 'user-del', data.USER1])
        multihost.master.qerun(['ipa', 'service-del', data.SERVICE1])
    request.addfinalizer(teardown_session)
