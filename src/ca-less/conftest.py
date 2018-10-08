""" Conftest for server install """
import pytest
from ipa_pytests.qe_class import multihost
from ipa_pytests.qe_install import uninstall_server
from ipa_pytests.qe_class import qe_use_class_setup


def pytest_namespace():
    """ Define the number of test host roles using namespace hook """
    return {'num_replicas': 1,
            'num_clients': 0,
            'num_others': 0,
            'num_ads': 0
            }


@pytest.fixture(scope="session", autouse=True)
def setup_session(request, multihost):

    multihost.replica = multihost.replicas[0]
    cmd = "dnf -y module install {}"
    multihost.master.run_command(cmd.format(multihost.master.config.server_module))
    multihost.replica.run_command(cmd.format(multihost.replica.config.server_module))
    def teardown_session():
        """ define fixture for session level teardown """
        pass

    request.addfinalizer(teardown_session)
