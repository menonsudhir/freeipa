# pylint: disable=R0801
""" IPA  BAckup Restore Conftest
conftest to setup required fixtures needed by tests:
- config for multihost plugin
"""

import pytest
from ipa_pytests.shared.server_utils import server_del
from ipa_pytests.qe_install import (setup_replica, uninstall_server,
                                    setup_client, set_etc_hosts,
                                    setup_master, uninstall_client)
from ipa_pytests.qe_class import multihost
from ipa_pytests.qe_class import qe_use_class_setup


def pytest_namespace():
    """ Define the number of test host roles using namespace hook """
    return {'num_replicas': 2,
            'num_clients': 2,
            'num_others': 0,
            'num_ads': 0}


@pytest.fixture(scope="module", autouse=True)
def setup_session(request, multihost):
    """ Setup session """
    # Defining convenience variables for multihost fixture
    # for replica and client
    multihost.replica1 = multihost.replicas[0]
    multihost.replica2 = multihost.replicas[1]
    multihost.client1 = multihost.clients[0]
    multihost.client2 = multihost.clients[1]
    try:
        setup_master(multihost.master)
        set_etc_hosts(multihost.replica1, multihost.master)
        set_etc_hosts(multihost.master, multihost.replica1)
        setup_replica(multihost.replica1, multihost.master,
                      setup_dns=True,
                      setup_ca=True,
                      setup_reverse=False)
        domain = multihost.master.domain.name

        setup_client(multihost.client1, multihost.master,
                     domain)
    except Exception as errval:
        print("Error in setup_session %s" % (str(errval.args[0])))
        pytest.skip("setup_session_skip")

    def teardown_session():
        """ define fixture for session level teardown """
        cmd_arg = ["kdestroy", "-A"]

        for client in multihost.clients:
            client.run_command(cmd_arg, raiseonerr=False)
            uninstall_client(client)

        for replica in multihost.replicas:
            replica.run_command(cmd_arg, raiseonerr=False)
            uninstall_server(replica)
            server_del(multihost.master,
                   hostname=replica.hostname,
                   force=True)

        uninstall_server(multihost.master)
        args = "lsof -i tcp:8443 | awk 'NR!=1 {print $2}' | xargs kill"
        print("Running : %s"%args)
        multihost.master.run_command(args, raiseonerr=False)
    request.addfinalizer(teardown_session)
