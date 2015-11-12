""" qe_class library:
qe_class provides the expansion to the multihost plugin for IPA testing
"""

import pytest
import pytest_multihost.config
import pytest_multihost.host
from pytest_multihost import make_multihost_fixture
from ipa_pytests.shared.logger import log


class QeConfig(pytest_multihost.config.Config):
    """
    QeConfig subclass of multihost plugin config to extend functionality
    for IPA testing.
    """
    extra_init_args = {'admin_id': '',
                       'admin_pw': '',
                       'dirman_id': '',
                       'dirman_pw': '',
                       'base_dn': '',
                       'dns_forwarder': ''}

    def __init__(self, **kwargs):
        """
        initialize additional variables to class support for testing.
        """
        super(QeConfig, self).__init__(**kwargs)
        self.admin_id = kwargs.get('admin_id') or 'admin'
        self.admin_pw = kwargs.get('admin_pw') or 'Secret123'
        self.dirman_id = kwargs.get('dirman_id') or '"cn=Directory Manager"'
        self.dirman_pw = kwargs.get('dirman_pw') or 'Secret123'
        self.dns_forwarder = kwargs.get('dns_forwarder') or '8.8.8.8'

    def get_domain_class(self):
        """
        return custom domain class.  This is needed to fully extend the config for
        custom multihost plugin extensions.
        """
        return QeDomain

    def to_dict(self, _autosave_names=()):
        """
        adds new args to the config dictionary that is used by multihost plugin
        """
        result = super(QeConfig, self).to_dict(self.extra_init_args)
        return result


class QeDomain(pytest_multihost.config.Domain):
    """
    QeDomain subclass of multihost plugin domain class.
    """
    def __init__(self, config, name, domain_type):
        """
        initialize new vars for IPA extensions to multihost plugin
        """
        super(QeDomain, self).__init__(config, name, domain_type)
        self.type = str(domain_type)
        self.config = config
        self.name = str(name)
        self.hosts = []
        self.realm = self.name.upper()
        self.basedn = '"' + "dc=" + ",dc=".join(self.name.split(".")) + '"'

    def get_host_class(self, host_dict):
        """
        return custom host class.  This is needed to fully extend the config for
        custom multihost plugin extensions.
        """
        return QeHost


class QeHost(pytest_multihost.host.Host):
    """
    QeHost subclass of multihost plugin host class.  This extends functionality
    of the host class for IPA QE purposes.  Here we add support functions that
    will be very widely used across tests and must be run on any or all hosts
    in the environment.
    """
    def run_hostname(self):
        """
        run_hostname :: <no arguments>
        - This is a test function simply to execute hostname command on a remote
        host.
        """
        cmd = self.run_command('hostname')
        print cmd.stdout_text

    def kinit_as_user(self, user, passwd):
        """
        kinit_as_user :: <user> <password>
        - executes kinit as the user provided.
        - <user> - krb principal user name.  can be just name or full principal
        - <password> - krb password for <uesr>
        """
        self.run_command('kdestroy -A')
        self.run_command(['kinit', user], stdin_text=passwd)
        cmd = self.run_command('klist')
        print cmd.stdout_text

    def kinit_as_admin(self):
        """
        kinit_as_admin :: <no arguments>
        - executes kinit as the IPA admin user.
        """
        self.kinit_as_user(self.config.admin_id, self.config.admin_pw)

    def qerun(self, command, stdin_text=None, exp_returncode=0, exp_output=None):
        """
        qerun :: <command> [stdin_text=<string to pass as stdin>]
                 [exp_returncode=<retcode>]
                 [<exp_output=<string to check from output>]
        - function to run a command and check return code and output
        """
        print "QERUN: %s" % " ".join(command)
        cmd = self.run_command(command, stdin_text, raiseonerr=False)
        print "------------------- QERUN_STDOUT:\n %s" % cmd.stdout_text
        print "------------------- QERUN_STDERR:\n %s" % cmd.stderr_text

        if cmd.returncode != exp_returncode:
            print "GOT: ", cmd.returncode
            print "EXPECTED: ", exp_returncode
            pytest.xfail("returncode mismatch.")

        if exp_output is None:
            print "Not checking expected output"

        elif cmd.stdout_text.find(exp_output) == 0:
            print "GOT: ", cmd.stdout_text
            print "EXPECTED: ", exp_output
            pytest.xfail("expected output not found")

        print "COMMAND SUCCEEDED!"

    def yum_install(self, packages):
        """
        yum_install :: <packages>
        - installs package list passed in
        """
        yum_command = ['yum', '-y', '--nogpgcheck', 'install'] + packages
        cmd = self.run_command(yum_command, raiseonerr=False)
        print "STDOUT: ", cmd.stdout_text
        print "STDERR: ", cmd.stderr_text
        if cmd.returncode != 0:
            raise ValueError("yum install failed with error code=%s" % cmd.returncode)


@pytest.yield_fixture(scope="session", autouse=True)
def multihost(request):
    """ Mulithost plugin fixture for session scope """
    mh = make_multihost_fixture(
        request,
        descriptions=[
            {
                'type': 'ipa',
                'hosts': {
                    'master': 1,
                    'replica': pytest.num_replicas,
                    'client': pytest.num_clients,
                    'other': pytest.num_others,
                },
            },
        ],
        config_class=QeConfig,
    )
    mh.domain = mh.config.domains[0]
    [mh.master] = mh.domain.hosts_by_role('master')
    mh.replicas = mh.domain.hosts_by_role('replica')
    mh.clients = mh.domain.hosts_by_role('client')
    mh.others = mh.domain.hosts_by_role('other')
    mh.replica = mh.replicas[0]
    mh.client = mh.clients[0]

    yield mh


@pytest.fixture(scope="class", autouse=True)
def qe_use_class_setup(request, multihost):
    def qe_newline():
        print

    if hasattr(request.cls(), 'class_setup'):
        try:
            request.cls().class_setup(multihost)
        except Exception, errval:
            print str(errval.args[0])
            pytest.skip("class_setup_failed")
        request.addfinalizer(lambda: request.cls().class_teardown(multihost))
        request.addfinalizer(lambda: qe_newline())


@pytest.fixture(scope="function")
def qe_extra_print(request):
    print


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
