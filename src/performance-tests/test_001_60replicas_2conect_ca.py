"""
Test Automation for IDM against 60 Replicas with CA.
BZ:1274524
"""
import time
import timeit
import pytest
import os
import ipa_pytests.shared.user_utils
import ipa_pytests.shared.utils
from ipa_pytests.qe_class import multihost
from ipa_pytests.qe_install import setup_master, setup_replica, uninstall_server
from ipa_pytests.shared.utils import service_control


class Testmaster(object):
    """ Test Class """
    def class_setup(self, multihost):
        """ Setup for class """
        print("\nClass Setup")
        print"MASTER: ", multihost.master.hostname
        resource_count = os.getenv("RESOURCE_COUNT", 5)
        replica_count = (int(resource_count) - 1)
        if replica_count <= 0:
            pytest.xfail("Number of resources for replica is 0, thus exiting")
        print replica_count
        for i in range(replica_count):
            print"REPLICA:", multihost.replicas[i].hostname

    def test_user_add(self, multihost):
        for i in range(10001):
            user = 'user_'+str(i)
#            add_ipa_user(multihost.master, user, passwd=None, first='test', last=str(i))
            multihost.master.run_command('ipa user-add'+ user +'--first=test --last=user --random', raiseonerr=False)

    def test_topology_two_connected_ca(self, multihost):
        """ Setup replica for two connected topology with CA, it assumes master is already installed."""
        replica_count = os.getenv("REPLICA_COUNT", 5)
        service_control(multihost.master, 'firewalld', 'stop')
        master = multihost.master
        print "---------------------------"
        print "1. Starting First Line Topology"
        for i in range(replica_count):
            print "MASTER: ", master
            print "REPLICA: ", multihost.replicas[i]
            print "---------------------------"
            service_control(multihost.replicas[i], 'firewalld', 'stop')
            setup_replica(multihost.replicas[i], master, setup_ca=True)
            master = multihost.replicas[i]
        print "Completed First Line Topology"
        print "---------------------------"
        print "2. Starting Second Line Topology"
        master = multihost.master.hostname
        new = range(replica_count)
        for i in new[1::2]:
            print "MASTER: ", master
            print "REPLICA: ", multihost.replicas[i].hostname
            replica = multihost.replicas[i].hostname
            print "---------------------------"
            segment = 'Line1_seg_'+str(i)
            suf = 'domain'
            multihost.replicas[i].kinit_as_admin()
            multihost.replicas[i].qerun(['ipa', 'topologysegment-add', '--leftnode=' + master,
                                         '--rightnode=' + replica, suf, segment])
            master = multihost.replicas[i].hostname
        print "Completed Second Line Topology for even replicas"
        print "---------------------------"
        print "3. Starting Third Line Topology"
        master = multihost.replicas[0].hostname
        new = range(replica_count)
        for i in new[2::2]:
            print "MASTER: ", master
            print "REPLICA: ", multihost.replicas[i].hostname
            replica = multihost.replicas[i].hostname
            print "---------------------------"
            segment = 'Line2_seg_'+str(i)
            suf = 'domain'
            multihost.replicas[i].kinit_as_admin()
            multihost.replicas[i].qerun(['ipa', 'topologysegment-add', '--leftnode=' + master,
                                         '--rightnode=' + replica, suf, segment])
            master = multihost.replicas[i].hostname
        print "Completed Third Line Topology for odd replicas"
        print "---------------------------"
        print "4. Starting Final topology"
        master = multihost.master.hostname
        new = range(replica_count)
        i = new[-1]
        replica = multihost.replicas[i].hostname
        print "MASTER: ", master
        print "REPLICA: ", replica
        print "---------------------------"
        segment = 'Line_seg_final'
        suf = 'domain'
        multihost.replicas[i].kinit_as_admin()
        multihost.replicas[i].qerun(['ipa', 'topologysegment-add', '--leftnode=' + master,
                                     '--rightnode=' + replica, suf, segment])
        print "Completed Final Topology for master and last replica"

    def test_topology_two_connected_prfm_wo_ca(self, multihost):
        multihost.master.run_command('easy_install pip')
        multihost.master.run_command('pip install pssh')
        multihost.master.kinit_as_admin()
        multihost.master.run_command('ipa-replica-manage list | grep -v ' + multihost.master.hostname + '> /tmp/list.txt')
        multihost.master.run_command('cat /tmp/list.txt | cut -d":" -f1 > /tmp/list1.txt')
        multihost.master.run_command('while read line; do echo "$line:22"; done < /tmp/list1.txt > /tmp/list2.txt')
        print "------------------------------------------------------------"
        print "Testing if command executes on all systems"
        print "------------------------------------------------------------"
        cmd = multihost.master.run_command('pssh -h /tmp/list2.txt -l root -A \"ipa user-find user_1\"',
                                           stdin_text='Secret123',
                                           raiseonerr=False)
        print cmd.stdout_text

    def class_teardown(self, multihost):
        replica_count = os.getenv("REPLICA_COUNT", 5)
        for i in range(replica_count):
            multihost.master.kinit_as_admin()
            replica = multihost.replicas[i].hostname
            multihost.master.run_command('ipa replica-manage del -f', replica, raiseonerr=False)
        for i in range(replica_count):
            multihost.replicas[i].run_command('ipactl restart', raiseonerr=False)
            uninstall_server(multihost.replicas[i])
        pass
