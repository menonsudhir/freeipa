""" qe_class library:
qe_class provides the expansion to the multihost plugin for IPA testing.
"""

import logging
import yaml
import random
import pytest_multihost.config
import pytest_multihost.host
from pytest_multihost import make_multihost_fixture
import pytest
from ipa_pytests.shared.logger import log
import re
try:
    import logstash
    LOGSTASH_INSTALLED = True
except ImportError:
    LOGSTASH_INSTALLED = False

LOGSTASHCFG = '/opt/ipa_pytests/ipa_pytests_logstash_cfg.yaml'


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
                       'dns_forwarder': '',
                       'chrome_browser': '',
                       'browser': '',
                       'virtualdisplay': 0}

    def __init__(self, **kwargs):
        """
        initialize additional variables to class support for testing.
        """
        super(QeConfig, self).__init__(**kwargs)
        self.admin_id = kwargs.get('admin_id', 'admin')
        self.admin_pw = kwargs.get('admin_pw', 'Secret123')
        self.dirman_id = kwargs.get('dirman_id', '"cn=Directory Manager"')
        self.dirman_pw = kwargs.get('dirman_pw', 'Secret123')
        self.dns_forwarder = kwargs.get('dns_forwarder', '8.8.8.8')
        self.chrome_browser = kwargs.get('chrome_browser', '/usr/bin/google-chrome')
        self.browser = kwargs.get('browser', 'firefox')
        self.virtualdisplay = kwargs.get('virtualdisplay', 0)

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

    def qerun(self, command, stdin_text=None, exp_returncode=0, exp_output=None, user=None):
        """
        qerun :: <command> [stdin_text=<string to pass as stdin>]
                 [exp_returncode=<retcode>]
                 [exp_output=<string to check from output>]
                 [user=<user to run command>]
        - function to run a command and check return code and output
        - if user arg is set, will run command as this user via su
        """
        if type(command) is list:
            print "\nQERUN COMMAND: %s" % " ".join(command)
            su_command = ['su', '-', user, '-c', " ".join(command)]
        else:
            print "\nQERUN COMMAND: %s" % command
            su_command = 'su - %s -c "%s"' % (user, command)

        if user is None:
            cmd = self.run_command(command, stdin_text, raiseonerr=False)
        else:
            cmd = self.run_command(su_command, stdin_text, raiseonerr=False)

        all_output = cmd.stdout_text + cmd.stderr_text
        print "QERUN ALL OUTPUT:"
        print all_output

        if cmd.returncode != exp_returncode:
            print "GOT: ", cmd.returncode
            print "EXPECTED: ", exp_returncode
            pytest.xfail("returncode mismatch.")

        if exp_output is None:
            print "Not checking expected output"
        elif not re.search(exp_output, all_output):
            print "GOT: ", all_output
            print "EXPECTED: ", exp_output
            pytest.fail("expected output not found")
        else:
            print "GOT: %s" % exp_output

        print "QERUN COMMAND SUCCEEDED!"

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

    def expect(self, expect_script):
        """
        expect :: <expect_script>
        - expect_script passed in as a string for file contents.  Not a path to
        an expect file.
        - runs expect remotely with script passed in.
        """

        # First put script string to file on remote host
        rand_tag = ''.join(random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
                           for _ in range(10))
        exp_file = "/tmp/qe_pytest_expect_file" + rand_tag
        self.put_file_contents(exp_file, expect_script)

        print "----expect script start----"
        print expect_script
        print "----expect script end----"
        print "remote side expect script filename: " + exp_file

        # Next run expect
        cmd = self.run_command(['expect', '-f', exp_file], raiseonerr=False)
        print "----expect output start----"
        print cmd.stdout_text
        print cmd.stderr_text
        print "----expect output end----"
        return cmd.returncode


@pytest.fixture(scope="function", autouse=True)
def test_count(request):
    try:
        pytest.count += 1
    except:
        pytest.count = 0
    request.function.func_globals['TEST_COUNT'] = pytest.count


@pytest.yield_fixture(scope="session", autouse=True)
def multihost(request):
    """ Mulithost plugin fixture for session scope """
    if pytest.num_ads > 0:
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
                {
                    'type': 'ad',
                    'hosts': {
                        'ad': pytest.num_ads,
                    },
                },
            ],
            config_class=QeConfig,
        )
    else:
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

    mh.domain_ipa = mh.config.domains[0]
    [mh.master] = mh.domain_ipa.hosts_by_role('master')
    mh.replicas = mh.domain_ipa.hosts_by_role('replica')
    mh.clients = mh.domain_ipa.hosts_by_role('client')
    mh.others = mh.domain_ipa.hosts_by_role('other')

    if pytest.num_ads > 0:
        mh.domain_ad = mh.config.domains[1]
        mh.ads = mh.domain_ad.hosts_by_role('ad')

    yield mh


@pytest.fixture(scope="class", autouse=True)
def qe_use_class_setup(request, multihost):
    """ fixture to add specific class setup method name """
    def qe_newline():
        """ extra print after finalizer to cleanup output format """
        print

    if hasattr(request.cls(), 'class_setup'):
        try:
            request.cls().class_setup(multihost)
        except StandardError as errval:
            print str(errval)
            pytest.skip("class_setup_failed")
        if hasattr(request.cls(), 'class_teardown'):
            request.addfinalizer(lambda: request.cls().class_teardown(multihost))
            request.addfinalizer(lambda: qe_newline())  # pylint: disable=unnecessary-lambda
        else:
            print("Missing class_teardown method for "
                  "Test Case : %s" % request.cls().__class__.__name__)


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


@pytest.mark.tryfirst
# Pylint: disable=W0613
def pytest_runtest_makereport(item, call, __multicall__):  # pylint: disable=unused-argument
    """
    define pytest runtest_makereport to format test case name as it
    is reported in output and junit.   Also, we add an additional log
    entry to report skip on call phase when setup returns skip.
    """

    # execute all other hooks to obtain the report object
    rep = __multicall__.execute()

    if LOGSTASH_INSTALLED:
        # Write log entry for test case phase results.  This
        log_test_phase_results(rep)

        # Additional check and log here to write a "fake" log entry
        # This is done so we can see the call itself for reporting
        # purposes.  So we copy rep and change when and log new result.
        if rep.when == "setup" and rep.outcome == "skipped":
            newrep = rep
            newrep.when = "call"
            log_test_phase_results(newrep)

    if rep.when == "call":
        # Pylint: disable=W0212
        tc_name = item._obj.__doc__.strip().split('\n')[0]  # pylint: disable=protected-access
        for line in item._obj.__doc__.strip().split('\n'):  # pylint: disable=protected-access
            if "@Test:" in line:
                tc_name = line.strip().replace("@Test: ", "", 1)
                break
        rep.nodeid = tc_name

    return rep


def log_test_phase_results(report):
    """ function to write test results to logstash """
    test_nodeid = report.nodeid
    test_case_when = report.when
    result = report.outcome

    with open(LOGSTASHCFG) as ymlfile:
        cfg = yaml.load(ymlfile)

    host = cfg['logstash']['host']
    port = cfg['logstash']['port']

    test_logger = logging.getLogger('python-logstash-logger')
    test_logger.setLevel(logging.INFO)
    test_logger.addHandler(logstash.LogstashHandler(host, port, version=1))

    test_class = ""
    next_field = 2
    if test_nodeid.split('::')[2] == "()":
        test_class = test_nodeid.split('::')[1]
        next_field = 3
    test_case = test_nodeid.split('::')[next_field]

    extra = {
        'test_nodeid': test_nodeid,
        'test_suite': test_nodeid.split('::')[0].split('/')[1],
        'test_module': test_nodeid.split('::')[0].split('/')[2],
        'test_class': test_class,
        'test_case': test_case,
        'test_case_when': test_case_when,
        'test_case_result': result
    }

    test_logger.info('python-logstash: test extra fields', extra=extra)
    test_logger.handlers = []
