"""
Overview:
Test suite to verify rbac role-add option
"""
from __future__ import print_function
from ipa_pytests.qe_class import multihost  # pylint: disable=unused-import
from ipa_pytests.shared.role_utils import role_add_member, role_remove_member
from ipa_pytests.shared.user_utils import add_ipa_user, del_ipa_user
from ipa_pytests.shared.paths import IPA


class TestRoleAddMemberPositive(object):
    """
    Positive testcases related to role-add-member
    """
    role_name = "helpdesk"

    def class_setup(self, multihost):
        """
        Setup for class
        """
        print("\nClass Setup")
        print("MASTER: ", multihost.master.hostname)

    def test_0001_user_all(self, multihost):
        """
        IDM-IPA-TC : rbac : Test to add one user member using option all
        """
        login = "testuseradmin"
        firstname = "testuseradmin"
        lastname = "testuseradmin"
        password = "Secret123"
        add_ipa_user(multihost.master, login, password, firstname, lastname)
        multihost.master.kinit_as_admin()
        role_type = "--users"
        role_add_member(multihost.master, self.role_name,
                        [role_type + "=" + login,
                         '--all'])

    def test_0002_group_raw(self, multihost):
        """
        IDM-IPA-TC : rbac : Test to add one group member using option raw
        """
        multihost.master.kinit_as_admin()
        group_name = "testgroupadmin"
        group_desc = "--desc=testgroupadmin"
        multihost.master.run_command([IPA, 'group-add', group_name, group_desc])
        role_type = "--groups"
        role_add_member(multihost.master, self.role_name,
                        [role_type + "=" + group_name,
                         '--raw'])

    def test_0003_multiple_user_members(self, multihost):
        """
        IDM-IPA-TC : rbac : Test to add multiple user members
        """
        login_list = ["testuseradmin1", "testuseradmin2", "testuseradmin3"]
        password = "Secret123"
        member_list = []
        role_type = '--users='
        for user in login_list:
            add_ipa_user(multihost.master, user, password, user, user)
            member_list.append(role_type+user)
        multihost.master.kinit_as_admin()
        member_list.append('--all')
        role_add_member(multihost.master, self.role_name, member_list)

    def test_0004_multiple_group_members(self, multihost):
        """
        IDM-IPA-TC : rbac : Test to add multiple group members
        """
        multihost.master.kinit_as_admin()
        role_type = "--groups="
        member_list = []
        group_list = ["testgroupadmin1", "testgroupadmin2", "testgroupadmin3"]
        for group in group_list:
            multihost.master.run_command([IPA, 'group-add', group, '--desc='+group])
            member_list.append(role_type+group)
        member_list.append('--all')
        role_add_member(multihost.master, self.role_name,
                        member_list)

    def test_0005_multiple_host_members(self, multihost):
        """
        IDM-IPA-TC : rbac : Test to add multiple host members
        """
        host_list = ["testhostadmin1.", "testhostadmin2.", "testhostadmin3."]
        member_list = []
        role_type = "--hosts="
        for host in host_list:
            multihost.master.run_command([IPA, 'host-add', host+multihost.master.domain.name,
                                          '--force'])
            member_list.append(role_type + host + multihost.master.domain.name)
        member_list.extend(['--all'])
        role_add_member(multihost.master, self.role_name, member_list)

    def test_0006_multiple_hostgroup_members(self, multihost):
        """
        IDM-IPA-TC : rbac : Test to add multiple hostgroup members
        """
        hostgroup_list = ["testhostgroupadmin1", "testhostgroupadmin2", "testhostgroupadmin3"]
        member_list = []
        role_type = "--hostgroups="
        for hostgroup in hostgroup_list:
            multihost.master.run_command([IPA, 'hostgroup-add', hostgroup, '--desc='+hostgroup])
            member_list.append(role_type + hostgroup)
        member_list.append('--all')
        role_add_member(multihost.master, self.role_name, member_list)

    def test_0007_user_host_member(self, multihost):
        """
        IDM-IPA-TC : rbac : Test to add user and host member
        """
        login = "testuseradmin4"
        firstname = "testuseradmin4"
        lastname = "testuseradmin4"
        password = "Secret123"
        role_type_users = "--users="
        add_ipa_user(multihost.master, login, password, firstname, lastname)
        multihost.master.kinit_as_admin()
        host_name = "testhostadmin4."+multihost.master.domain.name
        role_type_hosts = "--hosts="
        multihost.master.run_command([IPA, 'host-add', host_name, '--force'])
        role_add_member(multihost.master, self.role_name,
                        [role_type_users + login,
                         role_type_hosts + host_name,
                         '--raw'])

    def test_0008_remove_user_member(self, multihost):
        """
        IDM-IPA-TC : rbac : Test to remove user members
        """
        login_list = ["--users=testuseradmin", "--users=testuseradmin1",
                      "--users=testuseradmin2", "--users=testuseradmin3",
                      "--users=testuseradmin4"]
        role_remove_member(multihost.master, self.role_name, login_list)
        for user in login_list:
            del_ipa_user(multihost.master, user.split("=")[1].strip())

    def test_0009_remove_group_member(self, multihost):
        """
        IDM-IPA-TC : rbac : Test to remove group members
        """
        group_list = ["--groups=testgroupadmin", "--groups=testgroupadmin1",
                      "--groups=testgroupadmin2", "--groups=testgroupadmin3"]
        role_remove_member(multihost.master, self.role_name, group_list)
        for group in group_list:
            multihost.master.run_command([IPA, 'group-del', group.split("=")[1].strip()])

    def test_0010_remove_host_member(self, multihost):
        """
        IDM-IPA-TC : rbac : Test to remove host members
        """
        host_list = ["testhostadmin1.", "testhostadmin2.", "testhostadmin3.", "testhostadmin4."]
        role_type = "--hosts="
        for host in host_list:
            role_remove_member(multihost.master, self.role_name,
                               [role_type + host + multihost.master.domain.name])
            multihost.master.run_command([IPA, 'host-del', host + multihost.master.domain.name])

    def test_0011_remove_hostgroup_member(self, multihost):
        """
        IDM-IPA-TC : rbac : Test to remove hostgroup members
        """
        hostgroup_list = ["--hostgroups=testhostgroupadmin1", "--hostgroups=testhostgroupadmin2",
                          "--hostgroups=testhostgroupadmin3"]
        role_remove_member(multihost.master, self.role_name, hostgroup_list)
        for hostgroup in hostgroup_list:
            multihost.master.run_command([IPA, 'hostgroup-del', hostgroup.split("=")[1].strip()])
