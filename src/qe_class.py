""" qe_class library:
qe_class provides the expansion to the multihost plugin for IPA testing.
"""

import logging
import os
import yaml
import random
from distutils.version import LooseVersion
import pytest_multihost.config
import pytest_multihost.host
from pytest_multihost import make_multihost_fixture
import pytest
from ipa_pytests.shared.logger import log
from ipa_pytests.shared import paths
import time
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
                       'net_name': '',
                       'ad_top_domain' : '',
                       'ad_sub_domain' : '',
                       'ad_ip': '',
                       'ad_sub_ip': '',
                       'ad_user': '',
                       'ad_pwd': '',
                       'ad_hostname': '',
                       'virtualdisplay': 0,
                       'upgrade_from': '',
                       'upgrade_to': '',
                       'skip': '',
                       'untrusted_certs': False,
                       'domain_level': 1,
                       }

    def __init__(self, **kwargs):
        """
        initialize additional variables to class support for testing.
        """
        super(QeConfig, self).__init__(**kwargs)
        self.admin_id = kwargs.get('admin_id', 'admin')
        self.admin_pw = kwargs.get('admin_pw', 'Secret123')
        self.dirman_id = kwargs.get('dirman_id', '"cn=Directory Manager"')
        self.dirman_pw = kwargs.get('dirman_pw', 'Secret123')
        self.dns_forwarder = kwargs.get('dns_forwarder', '10.76.33.229')
        self.chrome_browser = kwargs.get('chrome_browser', '/usr/bin/google-chrome')
        self.browser = kwargs.get('browser', 'firefox')
        self.virtualdisplay = kwargs.get('virtualdisplay', 0)
        self.net_name = kwargs.get('net_name', 'TESTRELM')
        self.ad_top_domain = kwargs.get('ad_top_domain', 'pne.qe')
        self.ad_sub_domain = kwargs.get('ad_sub_domain', 'chd.pne.qe')
        self.ad_ip = kwargs.get('ad_ip', '10.76.33.229')
        self.ad_subip = kwargs.get('ad_subip', '10.76.33.209')
        self.ad_user = kwargs.get('ad_user', 'Administrator')
        self.ad_pwd = kwargs.get('ad_pwd', 'Secret123')
        self.ad_hostname = kwargs.get('ad_hostname', 'win1.pne.qe')
        self.ad_sub_hostname = kwargs.get('ad_sub_hostname', 'win2.chd.pne.qe')
        self.upgrade_from = kwargs.get('upgrade_from', os.getenv('UPGRADE_FROM'))
        self.upgrade_to = kwargs.get('upgrade_to', os.getenv("UPGRADE_TO"))
        self.skip = kwargs.get('skip', 'True')
        self.untrusted_certs = kwargs.get('untrusted_certs', os.getenv('UNTRUSTED_CERTS', False))
        self.domain_level = kwargs.get('domain_level', os.getenv('DOMAIN_LEVEL', 1))

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

    def get_os_version(host):
        rel = "/etc/redhat-release"
        # Set default value
        rhel_ver_string = '72'
        # Copy contents of file in variable
        release_text = host.transport.get_file_contents(rel)
        # Form Python regex for OS version
        release_regex = re.compile(r"Red Hat.*([0-9])\.([0-9])")
        osver = release_regex.match(release_text)
        if osver:
            # if found, group 1 and 2 will have major and minor version
            rhel_ver_string = osver.group(1) + osver.group(2)
        return rhel_ver_string

    def kinit_as_user(self, user, passwd):
        """
        kinit_as_user :: <user> <password>
        - executes kinit as the user provided.
        - <user> - krb principal user name.  can be just name or full principal
        - <password> - krb password for <uesr>
        """
        self.run_command('kdestroy -A')
        self.run_command(['kinit', user], stdin_text=passwd, raiseonerr=False)
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
            msg = "\n> returncode mismatch."
            msg += "\n> GOT: {}".format(cmd.returncode)
            msg += "\n> EXPECTED: {}".format(exp_returncode)
            pytest.fail(msg, pytrace=False)

        if exp_output is None:
            print "Not checking expected output"
        elif not re.search(exp_output, all_output):
            msg = "\n> expected output not found."
            msg += "\n> GOT: {}".format(all_output.rstrip('\n'))
            msg += "\n> EXPECTED: {}".format(exp_output)
            pytest.fail(msg, pytrace=False)
        else:
            print "GOT: %s" % exp_output

        print "QERUN COMMAND SUCCEEDED!"

    def yum_install(self, packages):
        """
        yum_install :: <packages>
        - installs package list passed in
        """
        timestamp = time.strftime('%Y%m%d%H%M%S', time.localtime())
        yum_output = '/tmp/qe_pytest_yum_output.{}'.format(timestamp)
        yum_command = [paths.YUM, '-y', '--nogpgcheck', 'install'] + packages
        cmd = self.run_command(yum_command, raiseonerr=False)

        print "yum install output in {}".format(yum_output)

        with open(yum_output, 'w') as yum_out:
            yum_out.write('YUMCMD: {}'.format(' '.join(yum_command)))
            yum_out.write('STDOUT: {}'.format(cmd.stdout_text))
            yum_out.write('STDERR: {}'.format(cmd.stderr_text))

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
        return cmd

    def rpm_install_check(self, package):
        """
        rpm_install_check :: package
        - check if package is installed or not
        """
        rpm_command = ['rpm', '-q', package]
        cmd = self.run_command(rpm_command, raiseonerr=False)
        if cmd.returncode == 0:
            return 0
        else:
            print("Package [%s] is not installed" % (package))
            return 1


@pytest.fixture(scope="function", autouse=True)
def test_count(request):
    try:
        pytest.count += 1
    except:
        pytest.count = 0
    request.function.func_globals['TEST_COUNT'] = pytest.count


@pytest.yield_fixture(scope="session", autouse=True)
def multihost(request):
    """ Multihost plugin fixture for session scope """
    # Default values for SUTs
    num_masters = 1
    num_replicas = getattr(pytest, 'num_replicas', 0)
    num_clients = getattr(pytest, 'num_clients', 0)
    num_others = getattr(pytest, 'num_others', 0)
    num_ads = getattr(pytest, 'num_ads', 0)

    desc = [
        {
            'type': 'ipa',
            'hosts': {
                'master': num_masters,
                'replica': num_replicas,
                'client': num_clients,
                'other': num_others,
            },
        }
    ]

    if num_ads > 0:
        desc.extend([
            {
                'type': 'ad',
                'hosts': {
                    'ad': num_ads,
                },
            }
        ])

    mh = make_multihost_fixture(
        request,
        descriptions=desc,
        config_class=QeConfig,
    )

    mh.domain_ipa = mh.config.domains[0]
    [mh.master] = mh.domain_ipa.hosts_by_role('master')
    mh.replicas = mh.domain_ipa.hosts_by_role('replica')
    mh.clients = mh.domain_ipa.hosts_by_role('client')
    mh.others = mh.domain_ipa.hosts_by_role('other')

    if num_ads > 0:
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

    if item._obj.__doc__:  # pylint: disable=protected-access
        tc_name = item._obj.__doc__.strip().split('\n')[0]  # pylint: disable=protected-access
        for line in item._obj.__doc__.strip().split('\n'):  # pylint: disable=protected-access
            if "@Title:" in line:
                tc_name = line.strip().replace("@Title: ", "", 1)
                break
        rep.nodeid = '::'.join(rep.nodeid.split('::')[0:-1]) + \
                     '::' + tc_name
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
