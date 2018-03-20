"""
This is test suite for IPA Backup Restore
"""
import pytest
from ipa_pytests.qe_class import multihost
import time
from ipa_pytests.qe_install import (setup_replica, uninstall_server,
                                    setup_client, set_etc_hosts,
                                    setup_master, uninstall_client)
from ipa_pytests.shared.server_utils import server_del
from ipa_pytests.ipa_backup_restore import backup_lib
from ipa_pytests.ipa_backup_restore import restore_lib


class TestBZ1199060(object):
    """ Test Class """

    def class_setup(self, multihost):
        """ Setup for class """
        print("\nUsing following hosts for IPA Backup Restore testcases")
        print("*" * 80)
        print("MASTER: %s" % multihost.master.hostname)
        for replica in multihost.replicas:
            print("REPLICA: %s" % replica.hostname)

        for client in multihost.clients:
            print("CLIENT: %s" % client.hostname)

        print("*" * 80)


    def test_0017_bz1199060(self, multihost):
        """
        :Title: IDM-IPA-TC : Backup-Restore : IPA backup restore when replication not disabled
                            https://bugzilla.redhat.com/show_bug.cgi?id=1199060

        :Requirement: IDM-IPA-REQ :

        :Automation: Yes

        :casecomponent: ipa
        """
        backup_lib.add_data_before_backup(multihost)

        # Full backup with logs
        print("Executing backup")
        backup_path = backup_lib.backup(multihost.master, logs=True)
        backup_lib.data_check_after_backup(multihost.master,
                                           backup_path,
                                           logs=True)
        backup_lib.data_deletion_after_backup(multihost)
        uninstall_server(multihost.master, force=True)
        restore_lib.ipa_restore(multihost.master, backup_path)

        # cehck user on respective host
        restore_lib.bz_1199060(multihost)

    def class_teardown(self, multihost):
        """ Teardown for class """
        print("Cleanup")
        backup_lib.clear_data(multihost.master)


class TestIPARestoreDifferentServer(object):

    def class_setup(self, multihost):
        """ Setup for class """
        print("\nUsing following hosts for IPA Backup Restore testcases")
        print("*" * 80)
        print("MASTER: %s" % multihost.master.hostname)
        for replica in multihost.replicas:
            print("REPLICA: %s" % replica.hostname)

        for client in multihost.clients:
            print("CLIENT: %s" % client.hostname)

        print("*" * 80)

    def test_0018_restore_from_backup_of_other_server(self, multihost):
        """
        :Title: IDM-IPA-TC : Backup-Restore : IPA restore from backup taken on other server

        :Requirement: IDM-IPA-REQ :

        :Automation: Yes

        :casecomponent: ipa
        """
        # Full backup with logs
        print("Executing backup")
        backup_path = backup_lib.backup(multihost.master, logs=True)

        restore_lib.ipa_restore_on_other_server(multihost, backup_path)


    def class_teardown(self, multihost):
        """ Teardown for class """
        print("Cleanup")


class TestIPABackupRestoreMisc(object):
    """ Test Class """

    def class_setup(self, multihost):
        """ Setup for class """
        print("\nUsing following hosts for IPA Backup Restore testcases")
        print("*" * 80)
        print("MASTER: %s" % multihost.master.hostname)
        for replica in multihost.replicas:
            print("REPLICA: %s" % replica.hostname)

        for client in multihost.clients:
            print("CLIENT: %s" % client.hostname)

        print("*" * 80)


    def test_0019_backup_ipa_service_down(self, multihost):
        """
        :Title: IDM-IPA-TC : Backup-Restore : IPA backup when ipa service is down

        :Requirement: IDM-IPA-REQ :

        :Automation: Yes

        :casecomponent: ipa
        """
        # Data check before restore

        # backup scenario
        backup_path = backup_lib.backup_when_ipa_service_down(multihost.master)


    def test_0020_restore_ipa_from_corrupt_backup(self, multihost):
        """
        :Title: IDM-IPA-TC : Backup-Restore : IPA resstore from corrupt backup

        :Requirement: IDM-IPA-REQ :

        :Automation: Yes

        :casecomponent: ipa
        """
        backup_path = backup_lib.backup(multihost.master)
        restore_lib.ipa_restore_from_corrupt_backup(multihost.master, backup_path)


    def test_0021_backup_before_server_install(self, multihost):
        """
        :Title: IDM-IPA-TC : Backup-Restore : IPA backup before server installed

        :Requirement: IDM-IPA-REQ :

        :Automation: Yes

        :casecomponent: ipa
        """
        backup_lib.ipa_backup_before_IPA_configured(multihost.master)
