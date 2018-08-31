"""
Vault tests library
"""

from ipa_pytests.qe_install import setup_master  # pylint: disable=unused-import
from ipa_pytests.qe_install import setup_replica  # pylint: disable=unused-import
from ipa_pytests.shared.user_utils import add_ipa_user
from . import data  # pylint: disable=relative-import
import re


def setup_test_prereqs(multihost, prefix="test"):
    """ Setup Test Prerequisites """
    priv_vault = [prefix + '_vault_priv']
    user_vault = [prefix + '_vault_user', '--user=' + data.USER1]
    shared_vault = [prefix + '_vault_shared', '--shared']
    service_vault = [prefix + '_vault_service',
                     '--service=' + data.SERVICE1]

    multihost.master.kinit_as_admin()
    # Create users:
    for tuser in ['_user1', '_user2', '_user3']:
        add_ipa_user(multihost.master, prefix + tuser, data.PASSWORD)

    # Create services:
    for tservice in ['_service1', '_service2', '_service3']:
        runcmd = ['ipa', 'service-add', prefix + tservice + '/' + multihost.master.hostname]
        multihost.master.qerun(runcmd)

    # Create groups:
    for tgroup in ['_group1', '_group2', '_group3']:
        runcmd = ['ipa', 'group-add', '--desc=group', prefix + tgroup]
        multihost.master.qerun(runcmd)

    # Add users to groups:
    users = "--users={" + prefix + "_user1," + prefix + "_user2}"
    runcmd = "ipa group-add-member " + prefix + "_group1 " + users
    multihost.master.qerun(runcmd)

    users = "--users={" + prefix + "_user2," + prefix + "_user3}"
    runcmd = "ipa group-add-member " + prefix + "_group2 " + users
    multihost.master.qerun(runcmd)

    runcmd = "ipa group-add-member " + prefix + "_group3 " + users
    users = "--users={" + prefix + "_user1," + prefix + "_user3}"
    multihost.master.qerun(runcmd)

    # Add vaults needed for tests:
    runcmd = ['ipa', 'vault-add', '--type=standard'] + priv_vault
    multihost.master.qerun(runcmd)
    runcmd = ['ipa', 'vault-add', '--type=standard'] + user_vault
    multihost.master.qerun(runcmd)
    runcmd = ['ipa', 'vault-add', '--type=standard'] + shared_vault
    multihost.master.qerun(runcmd)
    runcmd = ['ipa', 'vault-add', '--type=standard'] + service_vault
    multihost.master.qerun(runcmd)


def teardown_test_prereqs(multihost, prefix="test"):
    """ Teardown Test Prerequisites """
    priv_vault = [prefix + '_vault_priv']
    user_vault = [prefix + '_vault_user', '--user=' + data.USER1]
    shared_vault = [prefix + '_vault_shared', '--shared']
    service_vault = [prefix + '_vault_service',
                     '--service=' + data.SERVICE1]

    multihost.master.kinit_as_admin()
    # delete users:
    for tuser in ['_user1', '_user2', '_user3']:
        runcmd = ['ipa', 'user-del', prefix + tuser]
        multihost.master.qerun(runcmd)

    # delete services:
    for tservice in ['_service1', '_service2', '_service3']:
        runcmd = ['ipa', 'service-del', prefix + tservice + '/' + multihost.master.hostname]
        multihost.master.qerun(runcmd)

    # delete groups:
    for tgroup in ['_group1', '_group2', '_group3']:
        runcmd = ['ipa', 'group-del', prefix + tgroup]
        multihost.master.qerun(runcmd)

    # Add vaults needed for tests:
    runcmd = ['ipa', 'vault-del'] + priv_vault
    multihost.master.qerun(runcmd)
    runcmd = ['ipa', 'vault-del'] + user_vault
    multihost.master.qerun(runcmd)
    runcmd = ['ipa', 'vault-del'] + shared_vault
    multihost.master.qerun(runcmd)
    runcmd = ['ipa', 'vault-del'] + service_vault
    multihost.master.qerun(runcmd)


def delete_all_vaults(host):
    """ function to delete all vaults for teardown """
    dvault = ""
    duser = ""
    dservice = ""

    host.kinit_as_admin()

    cmd = host.run_command(['ipa', 'vault-find', '--shared', '--sizelimit=10000'], raiseonerr=False)
    for line in cmd.stdout_text.split('\n'):
        if "Vault name:" in line:
            dvault = line.split()[2]
            host.run_command(['ipa', 'vault-del', '--shared', dvault], raiseonerr=False)

    cmd = host.run_command(['ipa', 'vault-find', '--users', '--sizelimit=10000'], raiseonerr=False)
    for line in cmd.stdout_text.split('\n'):
        if "Vault name:" in line:
            dvault = line.split()[2]
        elif "Vault user:" in line:
            duser = line.split()[2]
            host.run_command(['ipa', 'vault-del', '--user', duser, dvault], raiseonerr=False)
            dvault = ""
            duser = ""

    cmd = host.run_command(['ipa', 'vault-find', '--services', '--sizelimit=10000'], raiseonerr=False)
    for line in cmd.stdout_text.split('\n'):
        if "Vault name:" in line:
            dvault = line.split()[2]
        elif "Vault service:" in line:
            dservice = line.split()[2]
            host.run_command(['ipa', 'vault-del', '--service', dservice, dvault], raiseonerr=False)
            dvault = ""
            dservice = ""


def find_vault_containers(host, vault_type='users'):
    """ function to find all containers based on type """
    instance = "-".join(host.domain.realm.split('.'))
    uri = 'ldapi://%2fvar%2frun%2fslapd-' + instance + '.socket'
    search_base = 'cn=' + vault_type + ',cn=vaults,cn=kra,' + \
                  host.domain.basedn.replace('"', '')
    search = ['ldapsearch', '-o', 'ldif-wrap=no', '-LLQ', '-H', uri, '-b', search_base, 'cn']
    cmd = host.run_command(search, raiseonerr=False)

    if cmd.returncode != 0:
        print("WARNING: ldapsearch failed...returning empty list")
        return []

    output = cmd.stdout_text.split('\n')
    output = [line for line in output if not re.search('^$', line)]
    output = [line for line in output if "dn:" not in line]
    output = [line.replace('cn: ', '') for line in output]
    output = [line for line in output if not re.search('vers', line)]
    output = [line for line in output if not re.search('^' + vault_type + '$', line)]
    return output


def delete_all_vault_containers(host):
    """ function to delete all containers for teardown """
    service_vault_containers = find_vault_containers(host, vault_type='services')
    user_vault_containers = find_vault_containers(host, vault_type='users')

    for svc in service_vault_containers:
        runcmd = ['ipa', 'vaultcontainer-del', '--service=' + svc]
        host.qerun(runcmd)

    for uvc in user_vault_containers:
        runcmd = ['ipa', 'vaultcontainer-del', '--user=' + uvc]
        host.qerun(runcmd)


def safe_setup_master(master):
    """ helper function to conditionally setup master """
    fin = '/tmp/ipa_pytests_setup_master_done'
    if not master.transport.file_exists(fin):
        setup_master(master)
        master.put_file_contents(fin, 'x')
    else:
        print("IPA Master Setup has already run.  Skipping")


def safe_setup_replica(replica, master):
    """ helper function to conditionally setup replica """
    fin = '/tmp/ipa_pytests_setup_replica_done'
    if not replica.transport.file_exists(fin):
        setup_replica(replica, master)
        replica.put_file_contents(fin, 'x')
    else:
        print("IPA Replica Setup has already run.  Skipping")


def safe_setup_master_kra(master):
    """ helper function to conditionally setup kra on master """
    fin = '/tmp/ipa_pytests_setup_master_kra_done'
    if not master.transport.file_exists(fin):
        master.qerun(['ipa-kra-install', '-U', '-p', master.config.dirman_pw])
        master.put_file_contents(fin, 'x')
    else:
        print("IPA Master KRA Setup has already run.  Skipping")
