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


class TestIPABackupRestoreFullBackendInstance(object):
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
        print("*" * 80)


    def test_0009_backup_restore_full_backend_instance(self, multihost):
        """
        :Title: IDM-IPA-TC: Backup-Restore : IPA Full backup restore backend instance

        :Requirement: IDM-IPA-REQ :

        :Automation: Yes

        :casecomponent: ipa
        """
        #Full Backup scenario 1 :: Full backup
        backup_lib.add_data_before_backup(multihost)

        backup_path = backup_lib.backup(multihost.master, logs=True)
        backup_lib.data_check_after_backup(multihost.master,
                                           backup_path,
                                           logs=True)
        backup_lib.data_deletion_after_backup(multihost)

        # Data Restore scenario 1 :: Data restore from full
        # backup with valid ds instance and backend
        print("Data restore from full backup with valid ds"
              "instance and backend")
        restore_lib.ipa_restore(multihost.master, backup_path, instance=True)
        restore_lib.ipa_log_check_after_restore_and_reinit(multihost)

        # data check after restore
        restore_lib.ipa_data_check_after_restore(multihost)

    def test_0010_backend_instance_negative(self, multihost):
        """
        :Title: IDM-IPA-TC: Backup-Restore : IPA Full backup restore backend instance
                            related test cases (negative)

        :Requirement: IDM-IPA-REQ :

        :Automation: Yes

        :casecomponent: ipa
        """
        backup_path = backup_lib.backup(multihost.master, logs=True)

        # restore with invalid dirsrv instance
        restore_lib.restore_invalid_dirsrv_instance(multihost.master,
                                                      backup_path,
                                                      instance=True)

        # restoring data from with invalid ds instance and backend option
        restore_lib.restore_invalid_dirsrv_instance(multihost.master,
                                                      backup_path,
                                                      backend=True)

        # restoring data with invalid backend option
        restore_lib.restore_invalid_backend(multihost.master,
                                              backup_path,
                                              backend=True)
        # restoring data with valid instance and invalid backend option
        restore_lib.restore_invalid_backend(multihost.master,
                                              backup_path,
                                              instance=True)
    def class_teardown(self, multihost):
        """ Teardown for class """
        print("Cleanup")
        backup_lib.clear_data(multihost.master)


class TestIPABackupRestoreDataBackendInstance(object):
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
        print("*" * 80)


    def test_0011_backup_restore_data_backend_instance(self, multihost):
        """
        :Title: IDM-IPA-TC: Backup-Restore : IPA Data backup restore backend instance

        :Requirement: IDM-IPA-REQ :

        :Automation: Yes

        :casecomponent: ipa
        """
        backup_lib.add_data_before_backup(multihost)

        # Data Backup scenario 2 :: Data backup offline
        backup_path = backup_lib.backup(multihost.master, data=True)
        backup_lib.data_check_after_backup(multihost.master,
                                           backup_path,
                                           data=True)
        backup_lib.data_deletion_after_backup(multihost)

        # Data Restore scenario 2 :: Data restore from data backup
        # with valid ds instance and backend
        print("Data restore from data backup with valid ds instance "
              "and backend")
        restore_lib.ipa_restore(multihost.master, backup_path, instance=True)
        restore_lib.ipa_log_check_after_restore_and_reinit(multihost)

        # data check after restore
        restore_lib.ipa_data_check_after_restore(multihost)

        # clear data
        backup_lib.clear_data(multihost.master)


    def test_0012_backup_restore_backend_without_instance(self, multihost):
        """
        :Title: IDM-IPA-TC: Backup-Restore : IPA Data backup restore backend without instance

        :Requirement: IDM-IPA-REQ :

        :Automation: Yes

        :casecomponent: ipa
        """
        # Data Restore scenario 3 :: Data restore from data backup with
        # valid backend without ds instance
        backup_lib.add_data_before_backup(multihost)

        backup_path = backup_lib.backup(multihost.master, data=True)
        backup_lib.data_deletion_after_backup(multihost)

        # restore with userRoot backend
        restore_lib.ipa_restore(multihost.master, backup_path, backend_root=True)
        # restore with ipaca backend
        restore_lib.ipa_restore(multihost.master, backup_path, backend_ca=True)
        restore_lib.ipa_log_check_after_restore_and_reinit(multihost)

        # data check after restore
        restore_lib.ipa_data_check_after_restore(multihost)

    def class_teardown(self, multihost):
        """ Teardown for class """
        print("Cleanup")
        backup_lib.clear_data(multihost.master)


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


    def test_0014_backup_restore_custom_log(self, multihost):
        """
        :Title: IDM-IPA-TC : Backup-Restore : IPA Data restore from custom log

        :Requirement: IDM-IPA-REQ :

        :Automation: Yes

        :casecomponent: ipa
        """
        # Data check before restore
        backup_lib.add_data_before_backup(multihost)

        # Backup scenario 1
        print("Full backup with custom log file")
        backup_path = backup_lib.backup(multihost.master, custom_log=True)
        backup_lib.data_check_after_backup(multihost.master,
                                           backup_path,
                                           custom_log=True)
        backup_lib.data_deletion_after_backup(multihost)

        # restore scenario
        restore_lib.ipa_restore(multihost.master, backup_path, data=True)
        restore_lib.ipa_log_check_after_restore_and_reinit(multihost)

        # data check after restore
        restore_lib.ipa_data_check_after_restore(multihost)


    def test_0015_backup_restore_online_custom_log(self, multihost):
        """
        :Title: IDM-IPA-TC : Backup-Restore : IPA Data restore online from custom log backup

        :Requirement: IDM-IPA-REQ :

        :Automation: Yes

        :casecomponent: ipa
        """
        # Backup scenario
        print("Full backup with custom log file")
        backup_path = backup_lib.backup(multihost.master, custom_log=True)
        backup_lib.data_check_after_backup(multihost.master,
                                           backup_path,
                                           custom_log=True)
        backup_lib.data_deletion_after_backup(multihost)

        # restore scenario
        restore_lib.ipa_restore(multihost.master, backup_path, online=True)
        restore_lib.ipa_log_check_after_restore_and_reinit(multihost)

        # data check after restore
        restore_lib.ipa_data_check_after_restore(multihost)


    def class_teardown(self, multihost):
        """ Teardown for class """
        print("Cleanup")
        backup_lib.clear_data(multihost.master)
