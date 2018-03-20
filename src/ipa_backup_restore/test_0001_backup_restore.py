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


class TestIPABackupRestoreFull(object):
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


    def test_0001_backup_restore_full(self, multihost):
        """
        :Title: IDM-IPA-TC: Backup-Restore : IPA backup restore full

        :Requirement: IDM-IPA-REQ :

        :Automation: Yes

        :casecomponent: ipa
        """
        # add data before backup
        backup_lib.add_data_before_backup(multihost)

        # Full backup with logs
        print("Executing backup")
        backup_path = backup_lib.backup(multihost.master, logs=True)
        backup_lib.data_check_after_backup(multihost.master,
                                           backup_path,
                                           logs=True)
        backup_lib.data_deletion_after_backup(multihost)
        backup_lib.disable_replication_uninstall_master(multihost)

        # Restore scenario
        print("Executing restore")
        restore_lib.ipa_restore(multihost.master, backup_path)
        restore_lib.ipa_log_check_after_restore_and_reinit(multihost)

        # data check after restore
        restore_lib.ipa_data_check_after_restore(multihost)


    def class_teardown(self, multihost):
        """ Teardown for class """
        print("Cleanup")
        backup_lib.clear_data(multihost.master)


class TestIPABackupRestoreGPG(object):
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


    def test_0002_backup_restore_gpg(self, multihost):
        """
        :Title: IDM-IPA-TC: Backup-Restore : IPA backup restore full with gpg encryption
                            decryption related test cases

        :Requirement: IDM-IPA-REQ :

        :Automation: Yes

        :casecomponent: ipa
        """
        # add data before backup
        backup_lib.add_data_before_backup(multihost)

        # Full backup with gpg encryption
        print("Executing backup")
        return_list = backup_lib.backup(multihost.master, gpg=True)
        backup_path = return_list[0]
        gpg_keyring = str(return_list[1])
        backup_lib.data_check_after_backup(multihost.master,
                                           backup_path,
                                           gpg=True)
        backup_lib.data_deletion_after_backup(multihost)
        backup_lib.disable_replication_uninstall_master(multihost)

        # Restore scenario
        print("Executing restore")
        # gpg_keyring = ['/root/file'] , we are strinping first and last
        # 2 char from it to make it as /root/file
        restore_lib.ipa_restore(multihost.master, backup_path, gpg_keyring=gpg_keyring[2:-2])
        restore_lib.ipa_log_check_after_restore_and_reinit(multihost)

        # data check after restore
        restore_lib.ipa_data_check_after_restore(multihost)


    def class_teardown(self, multihost):
        """ Teardown for class """
        print("Cleanup")
        backup_lib.clear_data(multihost.master)


class TestIPABackupRestoreDataOffline(object):
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


    def test_0003_backup_restore_data_offline(self, multihost):
        """
        :Title: IDM-IPA-TC: Backup-Restore : IPA Data backup restore offline

        :Requirement: IDM-IPA-REQ :

        :Automation: Yes

        :casecomponent: ipa
        """
        backup_lib.add_data_before_backup(multihost)

        # Data Backup scenario 1 :: Data backup offline
        backup_path = backup_lib.backup(multihost.master, data=True)
        backup_lib.data_check_after_backup(multihost.master,
                                           backup_path,
                                           data=True)
        backup_lib.data_deletion_after_backup(multihost)

        # Restore scenario
        print("Executing restore")
        restore_lib.ipa_restore(multihost.master, backup_path)
        restore_lib.ipa_log_check_after_restore_and_reinit(multihost)

        # data check after restore
        restore_lib.ipa_data_check_after_restore(multihost)


    def class_teardown(self, multihost):
        """ Teardown for class """
        print("Cleanup")
        backup_lib.clear_data(multihost.master)


class TestIPABackupOfflineRestoreOnlineData(object):
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


    def test_0004_backup_offline_restore_online(self, multihost):
        """
        :Title: IDM-IPA-TC: Backup-Restore : IPA Data backup offline restore online

        :Requirement: IDM-IPA-REQ :

        :Automation: Yes

        :casecomponent: ipa
        """
        # Data Backup scenario 2 :: Data backup offline
        backup_lib.add_data_before_backup(multihost)

        # Data Backup scenario 1 :: Data backup offline
        backup_path = backup_lib.backup(multihost.master, data=True)
        backup_lib.data_check_after_backup(multihost.master,
                                           backup_path,
                                           data=True)
        backup_lib.data_deletion_after_backup(multihost)

        # Restore scenario
        print("Executing restore")
        restore_lib.ipa_restore(multihost.master, backup_path, online=True)
        restore_lib.ipa_log_check_after_restore_and_reinit(multihost)

        # data check after restore
        restore_lib.ipa_data_check_after_restore(multihost)


    def test_0005_backup_offline_restore_without_data_option(self, multihost):
        """
        :Title: IDM-IPA-TC: Backup-Restore : IPA Data backup offline restore without
                            --data optioon

        :Requirement: IDM-IPA-REQ :

        :Automation: Yes

        :casecomponent: ipa
        """
        backup_path = backup_lib.backup(multihost.master, data=True)

        # Restore scenario
        print("Executing restore")
        restore_lib.restore_without_data_option(multihost.master, backup_path)
        restore_lib.reinit_replica(multihost)


    def class_teardown(self, multihost):
        """ Teardown for class """
        print("Cleanup")
        backup_lib.clear_data(multihost.master)


class TestIPABackupRestoreDataOnline(object):
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

    def test_0006_backup_restore_online(self, multihost):
        """
        :Title: IDM-IPA-TC: Backup-Restore : IPA Data backup online without --data option

        :Requirement: IDM-IPA-REQ :

        :Automation: Yes

        :casecomponent: ipa
        """
        backup_lib.online_backup_without_data_option(multihost.master)


    def test_0007_backup_restore_online(self, multihost):
        """
        :Title: IDM-IPA-TC: Backup-Restore : IPA Data backup restore online

        :Requirement: IDM-IPA-REQ :

        :Automation: Yes

        :casecomponent: ipa
        """
        # Data Backup scenario 3 :: Data backup online
        backup_lib.add_data_before_backup(multihost)
        backup_path = backup_lib.backup(multihost.master, online=True)
        backup_lib.data_check_after_backup(multihost.master,
                                           backup_path,
                                           data=True)
        backup_lib.data_deletion_after_backup(multihost)

        # Restore scenario
        print("data restore online")
        restore_lib.ipa_restore(multihost.master, backup_path, online=True)
        restore_lib.ipa_log_check_after_restore_and_reinit(multihost)

        # data check after restore
        restore_lib.ipa_data_check_after_restore(multihost)


    def class_teardown(self, multihost):
        """ Teardown for class """
        print("Cleanup")
        backup_lib.clear_data(multihost.master)


class TestIPABackupOnlineRestoreOfflineData(object):
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


    def test_0008_backup_online_restore_offline(self, multihost):
        """
        :Title: IDM-IPA-TC: Backup-Restore : IPA Data backup online restore offline

        :Requirement: IDM-IPA-REQ :

        :Automation: Yes

        :casecomponent: ipa
        """
        # Data Backup scenario 4 :: Data backup online
        backup_lib.add_data_before_backup(multihost)
        backup_path = backup_lib.backup(multihost.master, online=True)
        backup_lib.data_check_after_backup(multihost.master,
                                           backup_path,
                                           data=True)
        backup_lib.data_deletion_after_backup(multihost)

        # Restore scenario
        print("Restoring data offline")
        restore_lib.ipa_restore(multihost.master, backup_path, data=True)
        restore_lib.ipa_log_check_after_restore_and_reinit(multihost)

        # data check after restore
        restore_lib.ipa_data_check_after_restore(multihost)


    def class_teardown(self, multihost):
        """ Teardown for class """
        print("Cleanup")
        backup_lib.clear_data(multihost.master)
