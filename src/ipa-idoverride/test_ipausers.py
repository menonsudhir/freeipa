from __future__ import print_function

"""
Overview:
SetUp Requirements:
"""

import pytest
from ipa_pytests.qe_class import multihost
from ipa_pytests.shared.utils import service_control
from ipa_pytests.shared.user_utils import *
from ipa_pytests.shared.idviews_lib import *


class Testidview(object):
    """ Test Class """

    def class_setup(self, multihost):
        """ Setup for class """
        print("Class setup")
        print("MASTER: ", multihost.master.hostname)
        print("CLIENT: ", multihost.client.hostname)

    def test_views_ipa_0001(self, multihost):
        """Adding user with uid option"""
        multihost.master.kinit_as_admin()
        user = 'vuser1'
        viewname = 'view1'
        uid = '77777'
        multihost.master.kinit_as_admin()
        add_ipa_user(multihost.master, user)
        idview_add(multihost.master, viewname)
        cmd = idoverrideuser_add(multihost.master, viewname, user, uid)
        print (cmd.stdout_text)
        assert 'UID: 77777' in cmd.stdout_text

    def test_views_ipa_0002(self, multihost):
        """Adding user override with same uid and gid"""
        user = 'vuser2'
        viewname = 'view2'
        uid = '1234567'
        gid = '1234567'
        multihost.master.kinit_as_admin()
        add_ipa_user(multihost.master, user)
        idview_add(multihost.master, viewname)
        cmd = idoverrideuser_add(multihost.master, viewname, user, uid, gid)
        print (cmd.stdout_text)
        assert 'UID: 1234567' in cmd.stdout_text
        assert 'GID: 1234567' in cmd.stdout_text

    def test_views_ipa_0003(self, multihost):
        """Adding user override with different uid and gid option"""
        user = 'vuser3'
        viewname = 'view3'
        uid = '1234567'
        gid = '1234568'
        multihost.master.kinit_as_admin()
        add_ipa_user(multihost.master, user)
        idview_add(multihost.master, viewname)
        cmd = idoverrideuser_add(multihost.master, viewname, user, uid, gid)
        print (cmd.stdout_text)
        assert 'UID: 1234567' in cmd.stdout_text
        assert 'GID: 1234568' in cmd.stdout_text

    def test_views_ipa_0004(self, multihost):
        """Adding user override with uid and login options"""
        user = 'vuser4'
        viewname = 'view4'
        uid = '11111'
        multihost.master.kinit_as_admin()
        add_ipa_user(multihost.master, user)
        idview_add(multihost.master, viewname)
        cmd = idoverrideuser_add(multihost.master, viewname='view4',
                                 user='vuser4', uid='11111', login='user4')
        print (cmd.stdout_text)
        assert 'User login: user4' in cmd.stdout_text
        assert 'UID: 11111' in cmd.stdout_text

    def test_views_ipa_0005(self, multihost):
        """Adding user override with uid and gecos options"""
        user = 'vuser5'
        viewname = 'view5'
        uid = '11112'
        multihost.master.kinit_as_admin()
        add_ipa_user(multihost.master, user)
        idview_add(multihost.master, viewname)
        cmd = idoverrideuser_add(multihost.master, viewname='view5',
                                 user='vuser5', uid='11112', gecos='test5')
        print (cmd.stdout_text)
        assert 'GECOS: test5' in cmd.stdout_text
        assert 'UID: 11112' in cmd.stdout_text

    def test_views_ipa_0006(self, multihost):
        """Adding user override with uid and homedir options"""
        user = 'vuser6'
        viewname = 'view6'
        uid = '11113'
        multihost.master.kinit_as_admin()
        add_ipa_user(multihost.master, user)
        idview_add(multihost.master, viewname)
        cmd = idoverrideuser_add(multihost.master, viewname='view6',
                                 user='vuser6', uid='11113',
                                 homedir='/home/test6')
        print (cmd.stdout_text)
        assert 'UID: 11113' in cmd.stdout_text
        assert 'Home directory: /home/test6' in cmd.stdout_text

    def test_views_ipa_0007(self, multihost):
        """Adding user override with uid and shell options"""
        user = 'vuser7'
        viewname = 'view7'
        uid = '11114'
        multihost.master.kinit_as_admin()
        add_ipa_user(multihost.master, user)
        idview_add(multihost.master, viewname)
        cmd = idoverrideuser_add(multihost.master, viewname='view7',
                                 user='vuser7', uid='11114', shell='/bin/bash')
        print (cmd.stdout_text)
        assert 'UID: 11114' in cmd.stdout_text
        assert 'Login shell: /bin/bash' in cmd.stdout_text

    def test_views_ipa_0009(self, multihost):
        """Adding user override with uid and desc options"""
        user = 'vuser9'
        viewname = 'view9'
        uid = '11116'
        multihost.master.kinit_as_admin()
        add_ipa_user(multihost.master, user)
        idview_add(multihost.master, viewname)
        cmd = idoverrideuser_add(multihost.master, viewname='view9',
                                 user='vuser9', uid='11116', desc='testing')
        print (cmd.stdout_text)
        assert 'UID: 11116' in cmd.stdout_text
        assert 'Description: testing' in cmd.stdout_text

    def test_views_ipa_0033(self, multihost):
        """Modifying user override description"""
        user = 'vuser10'
        viewname = 'view10'
        desc = 'changing desc'
        multihost.master.kinit_as_admin()
        add_ipa_user(multihost.master, user)
        idview_add(multihost.master, viewname)
        cmd1 = idoverrideuser_add(multihost.master, viewname='view10',
                                  user='vuser10', desc='test')
        print (cmd1.stdout_text)
        assert 'Added User ID override "vuser10"' in cmd1.stdout_text
        cmd2 = idoverrideuser_mod(multihost.master, viewname, user,
                                  desc='changing desc')
        print (cmd2.stdout_text)
        assert 'Description: changing desc' in cmd2.stdout_text

    def test_views_ipa_0034(self, multihost):
        """Modifying user override login"""
        user = 'vuser11'
        viewname = 'view11'
        login = 'user11'
        multihost.master.kinit_as_admin()
        add_ipa_user(multihost.master, user)
        idview_add(multihost.master, viewname)
        cmd1 = idoverrideuser_add(multihost.master, viewname='view11',
                                  user='vuser11', login='vuser')
        print (cmd1.stdout_text)
        assert 'Added User ID override "vuser11"' in cmd1.stdout_text
        cmd2 = idoverrideuser_mod(multihost.master, viewname, user,
                                  login='user11')
        print (cmd2.stdout_text)
        assert 'User login: user11' in cmd2.stdout_text

    def test_views_ipa_0035(self, multihost):
        """Modifying user override uid"""
        user = 'vuser12'
        viewname = 'view12'
        uid = '55555'
        multihost.master.kinit_as_admin()
        add_ipa_user(multihost.master, user)
        idview_add(multihost.master, viewname)
        cmd1 = idoverrideuser_add(multihost.master, viewname='view12',
                                  user='vuser12', uid='77777')
        print (cmd1.stdout_text)
        assert 'Added User ID override "vuser12"' in cmd1.stdout_text
        cmd2 = idoverrideuser_mod(multihost.master, viewname, user, uid)
        print (cmd2.stdout_text)
        assert 'UID: 55555' in cmd2.stdout_text

    def test_views_ipa_0036(self, multihost):
        """Modifying user override gecos"""
        user = 'vuser13'
        viewname = 'view13'
        gecos = 'test'
        multihost.master.kinit_as_admin()
        add_ipa_user(multihost.master, user)
        idview_add(multihost.master, viewname)
        cmd1 = idoverrideuser_add(multihost.master, viewname='view13',
                                  user='vuser13', gecos='test')
        print (cmd1.stdout_text)
        assert 'Added User ID override "vuser13"' in cmd1.stdout_text
        cmd2 = idoverrideuser_mod(multihost.master, viewname, user,
                                  gecos='testing gecos')
        print (cmd2.stdout_text)
        assert 'GECOS: testing gecos' in cmd2.stdout_text

    def test_views_ipa_0037(self, multihost):
        """Modifying user override gidnumber"""
        user = 'vuser14'
        viewname = 'view14'
        gidnumber = '88888'
        multihost.master.kinit_as_admin()
        add_ipa_user(multihost.master, user)
        idview_add(multihost.master, viewname)
        cmd1 = idoverrideuser_add(multihost.master, viewname='view14',
                                  user='vuser14', gid='88888')
        print (cmd1.stdout_text)
        assert 'Added User ID override "vuser14"' in cmd1.stdout_text
        cmd2 = idoverrideuser_mod(multihost.master, viewname, user,
                                  gid='77777')
        print (cmd2.stdout_text)
        assert 'GID: 77777' in cmd2.stdout_text

    def test_views_ipa_0038(self, multihost):
        """Modifying user override homedir"""
        user = 'vuser15'
        viewname = 'view15'
        homedir = '/home/test15'
        multihost.master.kinit_as_admin()
        add_ipa_user(multihost.master, user)
        idview_add(multihost.master, viewname)
        cmd1 = idoverrideuser_add(multihost.master, viewname='view15',
                                  user='vuser15', homedir='/home/test15')
        print (cmd1.stdout_text)
        assert 'Added User ID override "vuser15"' in cmd1.stdout_text
        cmd2 = idoverrideuser_mod(multihost.master, viewname,
                                  user, homedir='/home/vuser15')
        print (cmd2.stdout_text)
        assert 'Home directory: /home/vuser15' in cmd2.stdout_text

    def test_views_ipa_0039(self, multihost):
        """Modifying user override shell"""
        user = 'vuser16'
        viewname = 'view16'
        shell = '/bin/sh'
        multihost.master.kinit_as_admin()
        add_ipa_user(multihost.master, user)
        idview_add(multihost.master, viewname)
        cmd1 = idoverrideuser_add(multihost.master, viewname='view16',
                                  user='vuser16', shell='/bin/sh')
        print (cmd1.stdout_text)
        assert 'Added User ID override "vuser16"' in cmd1.stdout_text
        cmd2 = idoverrideuser_mod(multihost.master, viewname,
                                  user, shell='/bin/bash')
        print (cmd2.stdout_text)
        assert 'Login shell: /bin/bash' in cmd2.stdout_text

    def test_views_ipa_0042(self, multihost):
        """Adding ipa group and adding group override"""
        groupname = 'ipagroup1'
        viewname = 'gview1'
        multihost.master.kinit_as_admin()
        add_ipa_group(multihost.master, groupname)
        idview_add(multihost.master, viewname)
        cmd = idoverridegroup_add(multihost.master, viewname, groupname)
        print (cmd.stdout_text)
        assert 'Added Group ID override "ipagroup1"' in cmd.stdout_text

    def test_views_ipa_0043(self, multihost):
        """Adding ipa group and adding group override with gid"""
        groupname = 'ipagroup2'
        viewname = 'gview2'
        gid = '99998'
        multihost.master.kinit_as_admin()
        add_ipa_group(multihost.master, groupname)
        idview_add(multihost.master, viewname)
        cmd = idoverridegroup_add(multihost.master, viewname, groupname, gid)
        print (cmd.stdout_text)
        assert 'GID: 99998' in cmd.stdout_text

    def test_views_ipa_0044(self, multihost):
        """Adding ipa group and adding group override with desc """
        groupname = 'ipagroup3'
        viewname = 'gview3'
        desc = 'testing desc'
        multihost.master.kinit_as_admin()
        add_ipa_group(multihost.master, groupname)
        idview_add(multihost.master, viewname)
        cmd = idoverridegroup_add(multihost.master, viewname,
                                  groupname, desc='testing desc')
        print (cmd.stdout_text)
        assert 'Description: testing desc' in cmd.stdout_text

    def test_views_ipa_0045(self, multihost):
        """Adding ipa group and adding group override with gid and groupname"""
        groupname = 'ipagroup4'
        viewname = 'gview4'
        gid = '123456'
        multihost.master.kinit_as_admin()
        add_ipa_group(multihost.master, groupname)
        idview_add(multihost.master, viewname)
        cmd = idoverridegroup_add(multihost.master, viewname, groupname, gid)
        print (cmd.stdout_text)
        assert 'Anchor to override: ipagroup4' in cmd.stdout_text
        assert 'GID: 123456' in cmd.stdout_text

    def test_views_ipa_0046(self, multihost):
        """Modifying idoverride group with gid"""
        groupname = 'ipagroup5'
        viewname = 'gview5'
        gid = '111111'
        multihost.master.kinit_as_admin()
        cmd = add_ipa_group(multihost.master, groupname)
        print (cmd.stdout_text)
        idview_add(multihost.master, viewname)
        idoverridegroup_add(multihost.master, viewname, groupname)
        cmd1 = idoverridegroup_mod(multihost.master, viewname='gview5',
                                   groupname='ipagroup5', gid='111111')
        print (cmd1.stdout_text)
        print (cmd1.stderr_text)
        assert 'GID: 111111' in cmd1.stdout_text

    def test_views_ipa_0047(self, multihost):
        """Modifying idoverride groupname with groupname option"""
        groupname = 'ipagroup6'
        groupname1 = 'ipagroup66'
        viewname = 'gview6'
        multihost.master.kinit_as_admin()
        cmd = add_ipa_group(multihost.master, groupname)
        print (cmd.stdout_text)
        idview_add(multihost.master, viewname)
        idoverridegroup_add(multihost.master, viewname, groupname)
        print (cmd.stdout_text)
        print (cmd.stderr_text)
        add_ipa_group(multihost.master, groupname1)
        cmd1 = idoverridegroup_mod(multihost.master, viewname, groupname,
                                   newgrp='ipagroup66')
        print (cmd1.stdout_text)
        print (cmd1.stderr_text)
        assert 'Modified an Group ID override "ipagroup6"' in cmd1.stdout_text
        assert 'Group name: ipagroup66' in cmd1.stdout_text

    def test_views_ipa_0048(self, multihost):
        """Modifying idoverride groupname with groupname option"""
        groupname = 'ipagroup7'
        groupname1 = 'ipagroup77'
        gid = '111112'
        viewname = 'gview7'
        multihost.master.kinit_as_admin()
        cmd = add_ipa_group(multihost.master, groupname)
        print (cmd.stdout_text)
        idview_add(multihost.master, viewname)
        idoverridegroup_add(multihost.master, viewname, groupname)
        print (cmd.stdout_text)
        print (cmd.stderr_text)
        add_ipa_group(multihost.master, groupname1)
        cmd1 = idoverridegroup_mod(multihost.master, viewname, groupname,
                                   gid='111112', newgrp='ipagroup77')
        print (cmd1.stdout_text)
        print (cmd1.stderr_text)
        assert 'Modified an Group ID override "ipagroup7"' in cmd1.stdout_text
        assert 'Group name: ipagroup77' in cmd1.stdout_text
        assert 'GID: 111112' in cmd1.stdout_text

    def test_views_ipa_0049(self, multihost):
        """Modifying idoverride groupname with desc option"""
        groupname = 'ipagroup8'
        desc = 'testing desc'
        viewname = 'gview8'
        multihost.master.kinit_as_admin()
        cmd = add_ipa_group(multihost.master, groupname)
        print (cmd.stdout_text)
        idview_add(multihost.master, viewname)
        cmd1 = idoverridegroup_add(multihost.master, viewname, groupname)
        print (cmd1.stdout_text)
        print (cmd1.stderr_text)
        cmd2 = idoverridegroup_mod(multihost.master, viewname, groupname,
                                   desc='testing desc')
        print (cmd2.stdout_text)
        print (cmd2.stderr_text)
        assert 'Description: testing desc' in cmd2.stdout_text

    def test_views_0049(self, multihost):
        """idoverrideuser find with desc option"""
        multihost.master.kinit_as_admin()
        viewname = 'view9'
        desc = 'testing'
        cmd = idoverrideuser_find(multihost.master, viewname, desc)
        print (cmd.stdout_text)
        print (cmd.stderr_text)
        assert 'Description: testing' in cmd.stdout_text

    def test_views_0050(self, multihost):
        """idoverrideuser find with login option"""
        multihost.master.kinit_as_admin()
        viewname = 'view4'
        login = 'user4'
        cmd = idoverrideuser_find(multihost.master, viewname, login)
        print (cmd.stdout_text)
        print (cmd.stderr_text)
        assert 'User login: user4' in cmd.stdout_text

    def class_teardown(self, multihost):
        """Full suite teardown"""
