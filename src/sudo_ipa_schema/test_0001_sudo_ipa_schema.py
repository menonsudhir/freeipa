import pytest
from ipa_pytests.qe_class import multihost
from ipa_pytests.shared.user_utils import add_ipa_user, del_ipa_user
from ipa_pytests.shared.utils import (service_control)
from lib import (group_add_member, group_del, add_sudo_command, del_sudo_command, client_sudo_user_allowed, client_sudo_group_allowed, sudorule_add_permissive_options, sudorule_add_defaults, sudorule_del, sudorule_add_attr, sudorule_del_attr)

# Common username and password for all testcases
tusr1 = "mytestuser1"
tusr2 = "mytestuser2"
tdumusr = "mytestdummyuser"
tgrp1 = "mytestgroup1"
tgrp2 = "mytestgroup2"
tdumgrp = "mytestdummygroup"
tpwd = "Secret123"
tsudorule = "mytestsudorule"
tdumhost = "mytestdummyhost"
tcmd1 = "/bin/true"
tcmd2 = "/bin/echo"

class TestSudo(object):
    """ Test Class """

    def class_setup(self, multihost):
        """ Setup for class """
        multihost.realm = multihost.master.domain.realm
        multihost.admin_pw = multihost.master.config.admin_pw
        print("Using following hosts for Sudo IPA Schema testcases")
        print("MASTER: %s" % multihost.master.hostname)
        print("CLIENT: %s" % multihost.client.hostname)
        multihost.master.kinit_as_admin()
        #Add IPA user as member of ipa group
        for tusr in [tusr1, tusr2, tdumusr]:
            add_ipa_user(multihost.master, tusr, tpwd)

        group_add_member(multihost, tusr1, tgrp1)
        group_add_member(multihost, tusr2, tgrp2)
        group_add_member(multihost, tdumusr, tdumgrp)

        #Add sudo commands for tests
        for tcmd in [tcmd1, tcmd2]:
            add_sudo_command(multihost, tcmd)

        #Add sudo_provider = ipa in sssd.conf
        cmd = ['sed', '-i', '/id_provider = ipa/a sudo_provider = ipa', '/etc/sssd/sssd.conf']
        multihost.client.qerun(cmd)
        service_control(multihost.client, 'sssd', 'restart')
        #Disable compat plugin on server
        DSE_LDIF_PATH = '/etc/dirsrv/slapd-' + multihost.realm.replace('.','-')
        cmd = ['cp', '-af', DSE_LDIF_PATH + '/dse.ldif', DSE_LDIF_PATH + '/dse.ldif.bak']
        multihost.master.qerun(cmd)
        cmd = ['ldapdelete', '-x', '-D', 'cn=Directory Manager', '-w', multihost.admin_pw, '-r', 'cn=sudoers,cn=Schema Compatibility,cn=plugins,cn=config']
        multihost.master.qerun(cmd)

    def test_0001_sudo_ipa_schema_check_defaults_entry_support(self, multihost):
        """
        IDM-IPA-TC: Sudo IPA Schema: Check defaults entry support
        """
        client_sudo_user_allowed(multihost, tusr1, tusr2, tcmd1, exp_returncode=1, exp_output='no tty present')
        sudorule_add_permissive_options(multihost, tsudorule)
        client_sudo_user_allowed(multihost, tusr1, tusr2, tcmd1, exp_returncode=1, exp_output='no tty present')
        sudorule_add_defaults(multihost)
        client_sudo_user_allowed(multihost, tusr1, tusr2, tcmd1)
        sudorule_del(multihost, tsudorule)

    def test_0002_sudo_ipa_schema_check_sudo_user_attribute_support(self, multihost):
        """
        IDM-IPA-TC: Sudo IPA Schema: Check sudo user attribute support
        """
        sudorule_add_permissive_options(multihost, tsudorule, user_arg="")
        sudorule_add_attr(multihost, 'user', tsudorule, '--users', tusr2)
        client_sudo_user_allowed(multihost, tusr1, tusr2, tcmd1, exp_returncode=1, exp_output='not allowed to run sudo')
        sudorule_del_attr(multihost, 'user', tsudorule, '--users', tusr2)
        sudorule_add_attr(multihost, 'user', tsudorule, '--users', tusr1)
        client_sudo_user_allowed(multihost, tusr1, tusr2, tcmd1)
        sudorule_del_attr(multihost, 'user', tsudorule, '--users', tusr1)
        sudorule_add_attr(multihost, 'user', tsudorule, '--users', tdumusr)
        client_sudo_user_allowed(multihost, tusr1, tusr2, tcmd1, exp_returncode=1, exp_output='not allowed to run sudo')
        sudorule_del_attr(multihost, 'user', tsudorule, '--users', tdumusr)
        sudorule_add_attr(multihost, 'user', tsudorule, '--groups', tgrp2)
        client_sudo_user_allowed(multihost, tusr1, tusr2, tcmd1, exp_returncode=1, exp_output='not allowed to run sudo')
        sudorule_del_attr(multihost, 'user', tsudorule, '--groups', tgrp2)
        sudorule_add_attr(multihost, 'user', tsudorule, '--groups', tgrp1)
        client_sudo_user_allowed(multihost, tusr1, tusr2, tcmd1)
        sudorule_del_attr(multihost, 'user', tsudorule, '--groups', tgrp1)
        sudorule_add_attr(multihost, 'user', tsudorule, '--groups', tdumgrp)
        client_sudo_user_allowed(multihost, tusr1, tusr2, tcmd1, exp_returncode=1, exp_output='not allowed to run sudo')
        sudorule_del_attr(multihost, 'user', tsudorule, '--groups', tdumgrp)
        sudorule_del(multihost, tsudorule)

    def test_0003_sudo_ipa_schema_check_sudo_runasuser_attribute_support(self, multihost):
        """
        IDM-IPA-TC: Sudo IPA Schema: Check sudo runasuser attribute support
        """
        sudorule_add_permissive_options(multihost, tsudorule, runasuser_arg="", runasgroup_arg="")
        sudorule_add_attr(multihost, 'runasuser', tsudorule, '--users', tusr1)
        client_sudo_user_allowed(multihost, tusr1, tusr2, tcmd1, exp_returncode=1, exp_output='not allowed to execute')
        sudorule_del_attr(multihost, 'runasuser', tsudorule, '--users', tusr1)
        sudorule_add_attr(multihost, 'runasuser', tsudorule, '--users', tusr2)
        client_sudo_user_allowed(multihost, tusr1, tusr2, tcmd1)
        sudorule_del_attr(multihost, 'runasuser', tsudorule, '--users', tusr2)
        sudorule_add_attr(multihost, 'runasuser', tsudorule, '--users', tdumusr)
        client_sudo_user_allowed(multihost, tusr1, tusr2, tcmd1, exp_returncode=1, exp_output='not allowed to execute')
        sudorule_del_attr(multihost, 'runasuser', tsudorule, '--users', tdumusr)
        sudorule_add_attr(multihost, 'runasuser', tsudorule, '--group', tgrp1)
        client_sudo_user_allowed(multihost, tusr1, tusr2, tcmd1, exp_returncode=1, exp_output='not allowed to execute')
        sudorule_del_attr(multihost, 'runasuser', tsudorule, '--groups', tgrp1)
        sudorule_add_attr(multihost, 'runasuser', tsudorule, '--groups', tgrp2)
        client_sudo_user_allowed(multihost, tusr1, tusr2, tcmd1)
        sudorule_del_attr(multihost, 'runasuser', tsudorule, '--groups', tgrp2)
        sudorule_add_attr(multihost, 'runasuser', tsudorule, '--groups', tdumgrp)
        client_sudo_user_allowed(multihost, tusr1, tusr2, tcmd1, exp_returncode=1, exp_output='not allowed to execute')
        sudorule_del_attr(multihost, 'runasuser', tsudorule, '--groups', tdumgrp)
        sudorule_del(multihost, tsudorule)

    def test_0004_sudo_ipa_schema_check_sudo_runasgroup_attribute_support(self, multihost):
        """
        IDM-IPA-TC: Sudo IPA Schema: Check sudo runasgroup attribute support
        """
        sudorule_add_permissive_options(multihost, tsudorule, runasuser_arg="", runasgroup_arg="")
        sudorule_add_attr(multihost, 'runasgroup', tsudorule, '--groups', tgrp1)
        client_sudo_group_allowed(multihost, tusr1, tgrp2, tcmd1, exp_returncode=1, exp_output='not allowed to execute')
        sudorule_del_attr(multihost, 'runasgroup', tsudorule, '--groups', tgrp1)
        sudorule_add_attr(multihost, 'runasgroup', tsudorule, '--groups', tgrp2)
        client_sudo_group_allowed(multihost, tusr1, tgrp2, tcmd1)
        sudorule_del_attr(multihost, 'runasgroup', tsudorule, '--groups', tgrp2)
        sudorule_add_attr(multihost, 'runasgroup', tsudorule, '--groups', tdumgrp)
        client_sudo_group_allowed(multihost, tusr1, tgrp2, tcmd1, exp_returncode=1, exp_output='not allowed to execute')
        sudorule_del_attr(multihost, 'runasgroup', tsudorule, '--groups', tdumgrp)
        sudorule_del(multihost, tsudorule)

    def test_0005_sudo_ipa_schema_check_sudo_host_attribute_support(self, multihost):
        """
        IDM-IPA-TC: Sudo IPA Schema: Check sudo host attribute support
        """
        sudorule_add_permissive_options(multihost, tsudorule, host_arg="")
        sudorule_add_attr(multihost, 'host', tsudorule, '--hosts', multihost.client.hostname)
        client_sudo_user_allowed(multihost, tusr1, tusr2, tcmd1)
        sudorule_del_attr(multihost, 'host', tsudorule, '--hosts', multihost.client.hostname)
        sudorule_add_attr(multihost, 'host', tsudorule, '--hosts', tdumhost)
        client_sudo_user_allowed(multihost, tusr1, tusr2, tcmd1, exp_returncode=1, exp_output='not allowed to run sudo')
        sudorule_del_attr(multihost, 'host', tsudorule, '--hosts', tdumhost)
        sudorule_del(multihost, tsudorule)

    def test_0006_sudo_ipa_schema_check_sudo_command_attribute_support(self, multihost):
        """
        IDM-IPA-TC: Sudo IPA Schema: Check sudo command attribute support
        """
        sudorule_add_permissive_options(multihost, tsudorule, cmd_arg="")
        client_sudo_user_allowed(multihost, tusr1, tusr2, tcmd1, exp_returncode=1, exp_output='not allowed to execute')
        cmd = ['ipa', 'sudorule-mod', tsudorule, '--cmd=all']
        multihost.master.qerun(cmd)
        client_sudo_user_allowed(multihost, tusr1, tusr2, tcmd1)
        cmd = ['ipa', 'sudorule-mod', tsudorule, '--cmd=']
        multihost.master.qerun(cmd)
        sudorule_add_attr(multihost, 'allow-command', tsudorule, '--sudocmds', tcmd1)
        client_sudo_user_allowed(multihost, tusr1, tusr2, tcmd1)
        client_sudo_user_allowed(multihost, tusr1, tusr2, tcmd2, exp_returncode=1, exp_output='not allowed to execute')
        sudorule_del_attr(multihost, 'allow-command', tsudorule, '--sudocmds', tcmd1)
        sudorule_add_attr(multihost, 'deny-command', tsudorule, '--sudocmds', tcmd1)
        client_sudo_user_allowed(multihost, tusr1, tusr2, tcmd1, exp_returncode=1, exp_output='not allowed to execute')
        client_sudo_user_allowed(multihost, tusr1, tusr2, tcmd2, exp_returncode=1, exp_output='not allowed to execute')
        sudorule_del_attr(multihost, 'deny-command', tsudorule, '--sudocmds', tcmd1)
        sudorule_add_attr(multihost, 'allow-command', tsudorule, '--sudocmds', tcmd1)
        sudorule_add_attr(multihost, 'deny-command', tsudorule, '--sudocmds', tcmd1)
        client_sudo_user_allowed(multihost, tusr1, tusr2, tcmd1, exp_returncode=1, exp_output='not allowed to execute')
        sudorule_del_attr(multihost, 'allow-command', tsudorule, '--sudocmds', tcmd1)
        sudorule_del_attr(multihost, 'deny-command', tsudorule, '--sudocmds', tcmd1)
        sudorule_add_attr(multihost, 'deny-command', tsudorule, '--sudocmds', tcmd1)
        sudorule_add_attr(multihost, 'allow-command', tsudorule, '--sudocmds', tcmd1)
        client_sudo_user_allowed(multihost, tusr1, tusr2, tcmd1, exp_returncode=1, exp_output='not allowed to execute')
        sudorule_del_attr(multihost, 'deny-command', tsudorule, '--sudocmds', tcmd1)
        sudorule_del_attr(multihost, 'allow-command', tsudorule, '--sudocmds', tcmd1)
        sudorule_add_attr(multihost, 'allow-command', tsudorule, '--sudocmds', tcmd1)
        sudorule_add_attr(multihost, 'deny-command', tsudorule, '--sudocmds', tcmd2)
        client_sudo_user_allowed(multihost, tusr1, tusr2, tcmd1)
        client_sudo_user_allowed(multihost, tusr1, tusr2, tcmd2, exp_returncode=1, exp_output='not allowed to execute')
        sudorule_del(multihost, tsudorule)

    def class_teardown(self, multihost):
        """ Teardown for class """
        print("Class teardown for Sudo IPA Schema")
        multihost.master.kinit_as_admin()
        del_ipa_user(multihost.master, tusr1)
        del_ipa_user(multihost.master, tusr2)
        del_ipa_user(multihost.master, tdumusr)
        group_del(multihost, tgrp1)
        group_del(multihost, tgrp2)
        group_del(multihost, tdumgrp)
        del_sudo_command(multihost, tcmd1)
        del_sudo_command(multihost, tcmd2)
        cmd = ['sed', '-i', '/sudo_provider = ipa/d', '/etc/sssd/sssd.conf']
        multihost.client.qerun(cmd)
        service_control(multihost.client, 'sssd', 'restart')
        DSE_LDIF_PATH = '/etc/dirsrv/slapd-' + multihost.realm.replace('.','-')
        cmd = ['mv', '-f', DSE_LDIF_PATH + '/dse.ldif.bak', DSE_LDIF_PATH + '/dse.ldif']
        multihost.master.qerun(cmd)

