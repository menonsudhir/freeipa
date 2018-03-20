""""Helper Function for Restore"""

import string
import os
import time
import re
import pytest

from ipa_pytests.shared.user_utils import (add_ipa_user, del_ipa_user,
                                           show_ipa_user, find_ipa_user)
from ipa_pytests.qe_install import (setup_replica, uninstall_server,
                                    setup_client, set_etc_hosts)
from ipa_pytests.shared import paths
from ipa_pytests.ipa_backup_restore.backup_lib import ipa_user_check

testuser1 = "testuser1"
testuser2 = "testuser2"
testuser3 = "testuser3"
testuser4 = "testuser4"
twentyseconds = 20


def resotre_invalid_keyring(host, backup_path):
    tmp = '/tmp/tmp.ipa_restore_encrypted_full.out'
    dirman_password = host.config.dirman_pw
    cmd_arg = [paths.IPARESTORE, backup_path,
               "--gpg-keyring=/root/backup1", ">", tmp, " 2>&1"]
    print("Restoring full backup with invalid key")
    cmd = host.run_command(cmd_arg,
            stdin_text=dirman_password + '\nyes', raiseonerr=False)
    assert cmd.returncode != 0
    print(cmd.stderr_text)
    print("Success : IPA restore failed with invalid gpg-keyring")


def restore_without_data_option(host, backup_path):
    dirman_password = host.config.dirman_pw
    print("Restoring data from data backup without --data option")
    cmd_arg = [paths.IPARESTORE, backup_path]
    print("Running : " + str(cmd_arg))
    cmd = host.run_command(cmd_arg,
            stdin_text=dirman_password + '\nyes')
    assert cmd.returncode == 0
    print(cmd.stdout_text)
    print("Success : Restoring data from data backup "
          "without --data option")


def ipa_restore(host, backup_path, **kwargs):
    """method for ipa restore"""
    dirman_password = host.config.dirman_pw
    cmd_arg = [paths.IPARESTORE, backup_path]

    gpg_keyring = kwargs.get('gpg_keyring', None)
    online = kwargs.get('--online', False)
    data = kwargs.get('--data', False)
    instance = kwargs.get('--instance', False)
    backend_root = kwargs.get('backend_root', False)
    backend_ca = kwargs.get('backend_ca', False)

    if gpg_keyring:
        # scenario: restore with invalid gpg-keyring
        resotre_invalid_keyring(host, backup_path)

        cmd_arg.append('--gpg-keyring=%s'%gpg_keyring)
        print("Restoring full backup with gpg-keyring")

    if online:
        print("ipa restore online")
        cmd_arg.append('--data')
        cmd_arg.append('--online')

    if data:
        print("IPA restore offline")
        cmd_arg.append('--data')

    if instance:
        print("IPA restore with valid backend and instance")
        ds_instance = host.domain.realm.replace(".", '-')
        cmd_arg.append('--data')
        cmd_arg.append('--backend=userRoot')
        cmd_arg.append('--instance=%s'%ds_instance)

    if backend_root:
        print("IPA restore with valid backend userRoot only")
        cmd_arg.append("--data")
        cmd_arg.append("--backend=userRoot")

    if backend_ca:
        print("IPA restore with valid backend ipaca only")
        cmd_arg.append("--data")
        cmd_arg.append("--backend=ipaca")

    print("Running : " + str(cmd_arg))
    dirman_password = host.config.dirman_pw
    cmd = host.run_command(cmd_arg,
            stdin_text=dirman_password + '\nyes')
    assert cmd.returncode == 0
    print(cmd.stdout_text)
    print("Success : IPA Master restored on %s"%host.hostname)
    time.sleep(twentyseconds)


def restore_invalid_dirsrv_instance(host, backup_path, instance=False, backend=False):
    invalid_instance = "TESTRELM-TEST1"
    dirman_password = host.config.dirman_pw
    cmd_arg = [paths.IPARESTORE, backup_path,
               "--data"]

    if instance:
        print("Restoring data from full backup with invalid instance")
        cmd_arg.append("--instance=%s"%invalid_instance)

    if backend:
        print("Restoring data from full backup with invalid ds instance"
          " and backend option")
        cmd_arg.append("--instance=%s"%invalid_instance)
        cmd_arg.append("--backend=userRoot")

    print("Running : " + str(cmd_arg))
    cmd = host.run_command(cmd_arg,
            stdin_text=dirman_password + '\nyes', raiseonerr=False)
    assert cmd.returncode != 0
    assert "Instance %s does not exist"%invalid_instance in cmd.stderr_text
    print("Success : IPA restore failed with invalid instance")


def restore_invalid_backend(host, backup_path, instance=False, backend=False):
    print("Restoring data from full backup with valid instance and"
          " invalid backend option")
    ds_instance = host.domain.realm.replace(".", '-')
    dirman_password = host.config.dirman_pw
    cmd_arg = [paths.IPARESTORE, backup_path, "--data"]
    if instance:
        print("Restoring data from full backup with valid instance and"
              " invalid backend option")

        cmd_arg.append("--instance=%s"%ds_instance)
        cmd_arg.append("--backend=userRoot1")

    if backend:
        cmd_arg.append('--backend=userRoot1')

    print("Running : " + str(cmd_arg))
    cmd = host.run_command(cmd_arg,
            stdin_text=dirman_password + '\nyes', raiseonerr=False)
    assert cmd.returncode != 0
    assert "Backend userRoot1 does not exist" in cmd.stderr_text
    print("Success : IPA restore failed with invalid backend option")


def reinit_replica(multihost):
    dirman_password = multihost.master.config.dirman_pw
    print("re-initializing %s in replication agreement after %s restore"%(
          multihost.replica1.hostname, multihost.master.hostname))
    cmd_arg = ['ipa-replica-manage', 're-initialize',
               '--from=%s'%multihost.master.hostname]
    print("Running : " + str(cmd_arg))
    cmd = multihost.replica1.run_command(cmd_arg, stdin_text=dirman_password)
    assert cmd.returncode == 0
    print(cmd.stdout_text)

    cmd_arg = ['ipa-csreplica-manage', 're-initialize',
               '--from=%s'%multihost.master.hostname]
    print("Running : " + str(cmd_arg))
    cmd = multihost.replica1.run_command(cmd_arg, stdin_text=dirman_password)
    assert cmd.returncode == 0
    print(cmd.stdout_text)
    print("Success : re-initialize %s from %s"%(
          multihost.replica1.hostname, multihost.master.hostname))
    # wait for replication
    time.sleep(twentyseconds)


def ipa_log_check_after_restore_and_reinit(multihost):
    """ipa check after restore and re-intialize replica from master"""
    restore_log = multihost.master.transport.file_exists(paths.IPARESTORELOG)
    if restore_log:
        print("Restore log exists : %s"%paths.IPARESTORELOG)
    else:
        raise AssertionError('Restore log not found.!!')

    # reinit replica
    reinit_replica(multihost)


def ipa_data_check_after_restore(multihost):
    """data check after restore"""
    ipa_user_check(multihost.replica1, testuser2)
    print("Success : user %s found on %s after %s restore"%(
          testuser2, multihost.replica1.hostname, multihost.master.hostname))

    cmd = show_ipa_user(multihost.replica1, testuser4)
    assert cmd.returncode != 0
    print(cmd.stderr_text)
    print("Success : user %s not found on %s after %s restore"%(
          testuser4, multihost.replica1.hostname, multihost.master.hostname))

    ipa_user_check(multihost.master, testuser1)
    print("Success : user %s found on master after %s restore"%(
          testuser1, multihost.master.hostname))

    cmd = show_ipa_user(multihost.master, testuser3)
    assert cmd.returncode != 0
    print(cmd.stderr_text)
    print("Success : user %s not found on master after %s restore"%(
          testuser3, multihost.master.hostname))

    # check user on client after restore
    ipa_user_check(multihost.client1, testuser1)
    ipa_user_check(multihost.client1, testuser2)

def ipa_restore_from_corrupt_backup(host, backup_dir):
    """ipa restore from corrupt backup"""
    dirman_password = host.config.dirman_pw
    print("Removing ipa-full.tar file")
    cmd_arg = ["rm", "-rf", backup_dir + "/ipa-full.tar"]
    print("Running : " + str(cmd_arg))
    cmd = host.run_command(cmd_arg)
    assert cmd.returncode == 0
    print(cmd.stdout_text)
    print("Success : Removed %s/ipa-full.tar"%backup_dir)

    print("Restoring from full backup When ipa-full.tar is missing")
    cmd_arg = [paths.IPARESTORE, backup_dir]
    print("Running : " + str(cmd_arg))
    cmd = host.run_command(cmd_arg,
            stdin_text=dirman_password + '\nyes', raiseonerr=False)
    assert cmd.returncode != 0
    assert "Unable to find backup file in %s"%backup_dir in cmd.stderr_text
    print(cmd.stderr_text)


def bz_1199060(multihost):
    for user in testuser1,testuser2:
        ipa_user_check(multihost.master, user)
        print("Success : user %s found on %s after restore"%(
                user, multihost.master.hostname))

    for user in testuser3,testuser4:
        cmd = show_ipa_user(multihost.master, user)
        assert cmd.returncode != 0
        print(cmd.stderr_text)
        print("Success : user %s not found on %s after restore on %s"%(
                user, multihost.replica1.hostname, multihost.master.hostname))

    for user in testuser1, testuser2:
        cmd = show_ipa_user(multihost.replica1, user)
        assert cmd.returncode != 0
        print(cmd.stderr_text)
        print("Success : user %s not found on %s after restore on %s"%(
                user, multihost.replica1.hostname, multihost.master.hostname))

    for user in testuser3, testuser4:
        ipa_user_check(multihost.replica1, user)
        print("Success : user %s found on %s"%(
                user, multihost.replica1.hostname))


def ipa_restore_on_other_server(multihost, backup_dir):
    dirman_password = multihost.master.config.dirman_pw

    # copy backup files from master to replica
    header = os.path.join(backup_dir, "header")
    full_tar = os.path.join(backup_dir, "ipa-full.tar")
    header_contents = multihost.master.transport.get_file_contents(header)
    full_tar_contents = multihost.master.transport.get_file_contents(full_tar)
    multihost.replica2.run_command(['mkdir', '/tmp/backup/'])
    multihost.replica2.run_command(['touch', '/tmp/backup/header'])
    multihost.replica2.run_command(['touch', '/tmp/backup/ipa-full.tar'])
    multihost.replica2.put_file_contents('/tmp/backup/header', header_contents)
    multihost.replica2.put_file_contents('/tmp/backup/ipa-full.tar', full_tar_contents)
    print("Restoring data on %s from full backup taken on %s"%(
            multihost.replica2.hostname, multihost.master.hostname))
    cmd_arg = [paths.IPARESTORE,
               "--data", backup_dir]
    cmd = multihost.replica2.run_command(cmd_arg,
            stdin_text=dirman_password + '\nyes', raiseonerr=False)
    assert cmd.returncode != 0
    print(cmd.stderr_text)
