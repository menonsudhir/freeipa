"""
This is a quick test for bugzilla verification for bz1680039
"""
import time
from ipa_pytests.qe_class import multihost
from ipa_pytests.ipa_upgrade.utils import upgrade, modify_repo
from ipa_pytests.ipa_upgrade.constants import repo_urls
from ipa_pytests.qe_install import uninstall_server


def check_compat_plugin(host):
    # ['ldapsearch', '-xLLL', '-D', '"cn=Directory Manager"',
    #  '-w', 'Secret123',
    # '-b', 'cn=groups,cn=Schema Compatibility,cn=plugins,cn=config']
    # host.config.dirman_id substitute as '"cn=Directory Manager"'
    # while running in pipline and throws invalid credentials error
    # (see extra single quotes around directory manager)
    # Hence replacing with hardcoded value
    cmd_rg = ['ldapsearch', '-xLLL',
              '-D', "cn=Directory Manager",
              '-w', host.config.dirman_pw,
              '-b',
              "cn=groups,cn=Schema Compatibility,cn=plugins,cn=config"]
    result = host.run_command(cmd_rg)
    return(result.stdout_text)


class TestBugzilla(object):
    """ Test Class """
    def class_setup(self, multihost):
        """ Setup for class """

        print("Using following hosts for IPA server Upgrade testcases")
        print("*" * 80)
        print("MASTER: %s" % multihost.master.hostname)
        print("MASTER: %s" % multihost.replica.hostname)
        print("*" * 80)

    def test_schema_compat_attribute_bz1803165(self, multihost):
        """Test if schema-compat-entry-attribute is set

        This is to ensure if said entry is not set on older version
        and set after upgrade.
        It also checks if compat tree is disable.

        related: https://bugzilla.redhat.com/show_bug.cgi?id=1803165
        """
        master = multihost.master
        replica = multihost.replica

        # set nightly repo to pull latest packages
        repo_url = repo_urls["8.2.app"]
        modify_repo(master, 'rhelappstream',
                    repo_url, '/etc/yum.repos.d/rhel-8.2-appstream.repo')
        modify_repo(replica, 'rhelappstream',
                    repo_url, '/etc/yum.repos.d/rhel-8.2-appstream.repo')
        repo_url = repo_urls["8.2.base"]
        modify_repo(master, 'rhelbaseos',
                    repo_url, '/etc/yum.repos.d/rhel-8.2-baseos.repo')
        modify_repo(replica, 'rhelbaseos',
                    repo_url, '/etc/yum.repos.d/rhel-8.2-baseos.repo')

        entries = check_compat_plugin(master)
        # ipaexternalmember=%deref_r("member","ipaexternalmember") attribute
        # is getting truncate and was failing in assertion. Hence I am
        # asserting only the part of initial line and not whole value
        # for attribute here.
        value = r'ipaexternalmember=%deref_r("member"'
        assert value not in entries
        assert 'schema-compat-lookup-nsswitch' not in entries

        # check for entries on replica
        entries = check_compat_plugin(replica)
        assert value not in entries
        assert 'schema-compat-lookup-nsswitch' not in entries

        # Update the packages to latest version
        upgrade(master)
        time.sleep(50)
        upgrade(replica)

        # check for bz-1803165 if entry is set after upgrade
        entries = check_compat_plugin(master)
        assert value in entries
        assert 'schema-compat-lookup-nsswitch' not in entries

        entries = check_compat_plugin(replica)
        assert value in entries
        assert 'schema-compat-lookup-nsswitch' not in entries

    def class_teardown(self, multihost):
        """Full suite teardown """
        uninstall_server(multihost.replica)
        uninstall_server(multihost.master)
