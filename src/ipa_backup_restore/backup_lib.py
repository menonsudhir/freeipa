""""Helper Function for Backup Restore"""

import pytest
import time
import re
import os
import time
from tempfile import NamedTemporaryFile

from ipa_pytests.shared.user_utils import (add_ipa_user, del_ipa_user,
                                           show_ipa_user, find_ipa_user)
from ipa_pytests.qe_install import (setup_replica, uninstall_server,
                                    setup_client, set_etc_hosts)
from ipa_pytests.shared.utils import service_control
from ipa_pytests.shared import paths

testuser1 = "testuser1"
testuser2 = "testuser2"
testuser3 = "testuser3"
testuser4 = "testuser4"
tenseconds = 10


def  ipa_user_check(host, user):
    """check user on host"""
    result = show_ipa_user(host, user)
    assert result.returncode == 0
    print(result.stdout_text)


def user_add_check_replication(host1, host2, user):
    """check replication by adding user on host1 and listing it
    on other host"""

    print("creating %s on %s"%(user, host1.hostname))
    add_ipa_user(host1, user)
    # wait for replication
    time.sleep(tenseconds)

    # listing user added at host1 on host2
    ipa_user_check(host2, user)
    print("Success : user %s added on %s found on %s"%(
          user, host1.hostname, host2.hostname))


def user_del_check_replication(host1, host2, user):
    """check replication by deleting user on host1 and listing it
    on other host"""

    print("deleting %s on %s"%(user, host1.hostname))
    del_ipa_user(host1, user)
    # wait for replication
    time.sleep(tenseconds)

    # listing user deleted at host1 on host2
    cmd = show_ipa_user(host2, user)
    assert cmd.returncode != 0
    print(cmd.stderr_text)
    print("Success : user %s deleted on %s not found on %s"%(
          user, host1.hostname, host2.hostname))


def add_data_before_backup(multihost):
    """data add before backup"""
    user_add_check_replication(multihost.master, multihost.replica1, testuser1)
    user_add_check_replication(multihost.replica1, multihost.master, testuser2)

    # listing user on client
    ipa_user_check(multihost.client1, testuser1)
    ipa_user_check(multihost.client1, testuser2)
    print("Success: user added on master and replica found on clients")


def ipa_gpg_encryption(host):
    """method for gpg ecryption"""
    keygen = '/root/keygen'
    keygen1 = '/root/keygen1'
    keygen_content = """%echo Generating a standard key\n
                      Key-Type: RSA\n
                      Key-Length: 2048\n
                      Name-Real: IPA Backup root\n
                      Name-Comment: IPA Backup root\n
                      Name-Email: root@example.com\n
                      Expire-Date: 0\n
                      %pubring /root/backup.pub\n
                      %secring /root/backup.sec\n
                      %commit\n
                      %echo done"""

    keygen1_content = """%echo Generating a standard key\n
                        Key-Type: RSA\n
                        Key-Length: 1048\n
                        Name-Real: IPA Backup test\n
                        Name-Comment: IPA Backup test\n
                        Name-Email: test@example.com\n
                        Expire-Date: 0\n
                        %pubring /root/another_backup.pub\n
                        %secring /root/another_backup.sec\n
                        %commit\n
                        %echo done"""

    host.put_file_contents(keygen, keygen_content)
    host.put_file_contents(keygen1, keygen1_content)
    print("Generating gpg keys")
    cmd_arg = [paths.GPG, "--batch", "--gen-key", keygen]
    print("Running : " + str(cmd_arg))
    cmd = host.run_command(cmd_arg)
    assert cmd.returncode == 0
    print(cmd.stdout_text)
    print("Success : gpg key generated : %s"%keygen)

    print("Exporting valid gpg key")
    cmd_arg = [paths.GPG, "--no-default-keyring", "--secret-keyring",
               "/root/backup.sec", "--keyring", "/root/backup.pub",
               "--list-secret-keys"]
    print("Running : " + str(cmd_arg))
    cmd = host.run_command(cmd_arg)
    assert cmd.returncode == 0
    print(cmd.stdout_text)
    print("Success : gpg key exported")

    return ["/root/backup"]


def backup_without_gpg_encryption(host):
    """backup scenario for backup with invalid gpg-keyring"""
    tmp = '/tmp/temp.out'
    print("backup without providing gpg-keyring")
    cmd_arg = [paths.IPABACKUP, "--gpg", "--gpg-keyring=", ">", tmp, "2>&1"]
    print("Running : " + str(cmd_arg))
    cmd = host.run_command(cmd_arg, raiseonerr=False)
    assert cmd.returncode != 0
    print(cmd.stderr_text)
    print("Success : Backup failed with invalid gpg-keyring.!")


def backup_with_data_logs(host):
    cmd_arg = [paths.IPABACKUP, "--data", "--logs"]
    print("Running : " + str(cmd_arg))
    cmd = host.run_command(cmd_arg, raiseonerr=False)
    assert cmd.returncode != 0
    print(cmd.stderr_text)
    print("Success : ipa backup failed when --data and --logs "
          "specified together")


def online_backup_without_data_option(host):
    print("--online option without --data option")
    cmd_arg = [paths.IPABACKUP, "--online"]
    print("Running : " + str(cmd_arg))
    cmd = host.run_command(cmd_arg, raiseonerr=False)
    assert cmd.returncode != 0
    assert "You cannot specify --online without --data" in cmd.stderr_text
    print("Success : ipa backup failed without --data")


def backup(host, **kwargs):
    """Run backup on host, return the path to the backup directory"""
    args = [paths.IPABACKUP]

    gpg = kwargs.get('gpg', False)
    logs = kwargs.get('logs', False)
    data = kwargs.get('data', False)
    online = kwargs.get('online', False)
    custom_log = kwargs.get('custom_log', False)
    gpg_keyrings = None

    if logs:
        print("IPA backup with logs")
        args.append('--logs')

    if data:
        # scenrio : Backup with --data and --logs together
        backup_with_data_logs(host)

        print("IPA data backup")
        args.append('--data')

    if gpg:
        args.append('--gpg')
        # scenario: Backup with invalid gpg-keyring
        backup_without_gpg_encryption(host)

        print("IPA backup with gpg-keyring")
        gpg_keyrings = ipa_gpg_encryption(host)
        args.append('--gpg-keyring=%s'%gpg_keyrings[0])

    if online:
        print("IPA backup online")
        args.append('--data')
        args.append('--online')

    if custom_log:
        print("IPA backup with custom log")
        args.append('--log-file=/tmp/custom_ipabackup.log')


    print("Running : %s"%str(args))
    result = host.run_command(args)
    assert result.returncode == 0
    print("Success: IPA backup successfull")

    regex = re.compile('\n.*Backed\sup\sto\s(.*)\n')

    if custom_log:
        file_contents = host.transport.get_file_contents('/tmp/custom_ipabackup.log')
    else:
        file_contents = host.transport.get_file_contents(paths.IPABACKUPLOG)
    path = str(regex.search(file_contents).groups()[0])

    if path:
        if gpg_keyrings:
            return [path, gpg_keyrings]
        else:
            return path
    else:
        raise AssertionError('Backup directory not found in %s'%(paths.IPABACKUPLOG))


def data_check_after_backup(host, backup_path, **kwargs):
    """ipa data checkup after data backup"""

    path1 = os.path.join(backup_path, "header")
    path1 = host.transport.file_exists(path1)

    gpg = kwargs.get('gpg', False)
    data = kwargs.get('data', False)
    logs = kwargs.get('logs', False)
    custom_log = kwargs.get('custom_log', False)

    if gpg:
        path2 = os.path.join(backup_path, "ipa-full.tar.gpg")
        path2 = host.transport.file_exists(path2)
        assert path1 and path2

    if data:
        path2 = os.path.join(backup_path, "ipa-data.tar")
        path2 = host.transport.file_exists(path2)
        assert path1 and path2

    if logs or custom_log:
        path2 = os.path.join(backup_path, "ipa-full.tar")
        path2 = host.transport.file_exists(path2)
        assert path1 and path2

    print("Success: Backup files are present")


def data_deletion_after_backup(multihost):
    """fucntion for data deletion after backup"""
    # delete added user on master
    user_del_check_replication(multihost.master, multihost.replica1, testuser1)

    # add user on master after backup
    user_add_check_replication(multihost.master, multihost.replica1, testuser3)

    # delete added user on replica
    user_del_check_replication(multihost.replica1, multihost.master, testuser2)

    # add user on replica after backup
    user_add_check_replication(multihost.replica1, multihost.master, testuser4)

    # check deleted user on client
    for user in testuser1, testuser2:
        cmd = show_ipa_user(multihost.client1, user)
        assert cmd.returncode != 0
        print(cmd.stderr_text)
        print("Success : user %s deleted on master/replica not found on %s "%(
              user, multihost.client1.hostname))


def disable_replication_uninstall_master(multihost):
    """disable replication agreement and uninstall server"""

    # Disable replication agreement
    tf = NamedTemporaryFile()
    ldif_file = tf.name
    entry_ldif = (
        "dn: cn=meTo{hostname},cn=replica,"
        "cn=dc\\3Dtestrelm\\2Cdc\\3Dtest,cn=mapping tree,cn=config\n"
        "changetype: modify\n"
        "replace: nsds5ReplicaEnabled\n"
        "nsds5ReplicaEnabled: off\n\n"

        "dn: cn=caTo{hostname},cn=replica,"
        "cn=o\\3Dipaca,cn=mapping tree,cn=config\n"
        "changetype: modify\n"
        "replace: nsds5ReplicaEnabled\n"
        "nsds5ReplicaEnabled: off").format(
        hostname=multihost.replica1.hostname)
    multihost.master.put_file_contents(ldif_file, entry_ldif)

    # disable replication agreement
    arg = ['ldapmodify',
           '-h', multihost.master.hostname,
           '-p', '389', '-D',
           str(multihost.master.config.dirman_id),
           '-w', multihost.master.config.dirman_pw,
           '-f', ldif_file]
    print("running:%s"%str(arg))
    cmd = multihost.master.run_command(arg)
    assert cmd.returncode == 0
    time.sleep(tenseconds)

    # uninstall master
    print("Uninstalling IPA server: %s"%multihost.master.hostname)
    uninstall_server(multihost.master)


def ipa_backup_before_IPA_configured(host):
    # uninstall master
    uninstall_server(host, force=True)
    print("backup before IPA Configured")
    cmd_arg = [paths.IPABACKUP]
    print("Running : " + str(cmd_arg))
    cmd = host.run_command(cmd_arg, raiseonerr=False)
    assert cmd.returncode != 0
    assert "IPA is not configured on this system" in cmd.stderr_text
    print("Success : Unable to take backup if ipa is not configured")


def backup_when_ipa_service_down(host):
    cmd = service_control(host, "ipa", "stop")
    assert cmd.returncode == 0
    print(cmd.stdout_text)
    print("Success : IPA Server down")

    print("Taking full backup without logs")
    cmd_arg = [paths.IPABACKUP]
    print("Running : " + str(cmd_arg))
    cmd = host.run_command(cmd_arg)
    assert cmd.returncode == 0
    print(cmd.stdout_text)
    print("Success : IPA backup succeed")

    cmd = service_control(host, "ipa", "start")
    assert cmd.returncode == 0
    print(cmd.stdout_text)
    print("Success : IPA Server up")

    regex = re.compile('\n.*Backed\sup\sto\s(.*)\n')
    file_contents = host.transport.get_file_contents(paths.IPABACKUPLOG)
    path = str(regex.search(file_contents).groups()[0])

    if path:
        return path
    else:
        raise AssertionError('Backup directory not found in %s'%(paths.IPABACKUPLOG))

def clear_data(host):
    """method for user clean up"""
    for user in testuser1, testuser2:
        del_ipa_user(host, user)

    # clear logs
    for f in paths.IPABACKUPLOG,paths.IPARESTORELOG:
        args = ['rm', '-rf', f]
        print("Running : %s"%str(args))
        host.run_command(args)


def selinux_boolean(host, off):
    if off:
        print("Turning off the httpd_can_network_connect selinux boolean")
        cmd_arg = [paths.SETSEBOOL, "httpd_can_network_connect", "0"]
        print("Running : " + str(cmd_arg))
        cmd = host.run_command(cmd_arg)
        assert cmd.returncode == 0
        print("Success : boolean httpd_can_network_connect turned off")
        print("Turning off the httpd_manage_ipa selinux boolean")
        cmd_arg = [paths.SETSEBOOL, "httpd_manage_ipa", "0"]
        print("Running : " + str(cmd_arg))
        cmd = host.run_command(cmd_arg)
        assert cmd.returncode == 0
        print(cmd.stdout_text)
        print("Success : boolean httpd_manage_ipa turned off")

    else:
        cmd_arg = paths.GETSEBOOL + (" httpd_can_network_connect|"
                        "grep 'httpd_can_network_connect --> on'")
        print("Checking status of selinux boolean httpd_can_network_connect")
        print("Running : " + str(cmd_arg))
        cmd = host.run_command(cmd_arg)
        assert cmd.returncode == 0
        print(cmd.stdout_text)
        print("Success : boolean httpd_can_network_connect tunred ON after restore")

        print("Checking status of selinux boolean httpd_manage_ipa")
        cmd_arg = paths.GETSEBOOL + (" httpd_manage_ipa|"
                                   "grep 'httpd_manage_ipa --> on'")
        print("Running : " + str(cmd_arg))
        cmd = host.run_command(cmd_arg)
        assert cmd.returncode == 0
        print(cmd.stdout_text)
        print("Success : boolean httpd_manage_ipa tunred ON after restore")
