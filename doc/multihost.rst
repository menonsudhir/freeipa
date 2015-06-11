Multihost Plugin
================

Plugin setup and use
--------------------

This doc describes how to setup a config for the pytest multihost plugin.

- Example::

    ssh_key_filename: ~/.ssh/id_rsa
    admin_id: admin
    admin_pw: Secret123
    dirman_id: '"cn=Directory Manager"'
    dirman_pw: Secret123
    dns_forwarder: 192.168.122.1
    domains:
      - name: testrelm.test
        type: ipa
        hosts:
          - name: master.testrelm.test
            external_hostname: rhel7-1.example.com
            ip: 192.168.122.71
            role: master
          - name: replica.testrelm.test
            external_hostname: rhel7-2.example.com
            ip: 192.168.122.72
            role: replica
          - name: client.testrelm.test
            external_hostname: rhel7-3.example.com
            ip: 192.168.122.73
            role: client

- Fields
    - admin_id - IPA Admin principal ID
    - admin_pw - IPA Admin password
    - dirman_id - IPA Directory Server Manager ID
    - dirman_pw - IPA Directory Server Manager password
    - dns_forwarder - DNS forwarder for cases where DNS is setup
    - domains - defines config for the 
        - name - name of domain.  This is DNS and IPA domain name
        - type - should be ipa for most
        - hosts - defines hosts in test environment
            - name - name of host in environment.  not necessarily real name
            - external_hostname - needed if name differs.
            - ip - ip address of host.
            - role - this is the role.  should be master, replica, client, or 
              similar.

- Typical Setup
    - Set dns_forwarder to the appropriate value.  By default the qe_install
      setup functions configures DNS.  In most cases, you can just use the
      first nameserver from /etc/resolv.conf.
    - Make sure that there is a host defined for each node needed by the test.
    - Set 'name' if you don't want to use ones listed in config examples.
    - set 'ip' if it is not actually resolvable
    - set external_hostname if it is resolved differently from you point of 
      origin.
    - make sure role is set to match what is needed by the test

Using the plugin in tests
-------------------------

The plugin (and qe_class extensions) provide a framework for multi-host testing.
There are some typical uses that are described here.

- Test Environment variables (and defaults)::

    mulithost.<host_by_role>.config.admin_id = admin
    mulithost.<host_by_role>.config.admin_pw = Secret123
    mulithost.<host_by_role>.config.dirman_id = cn=Directory Manager
    mulithost.<host_by_role>.config.dirman_pw = Secret123
    mulithost.<host_by_role>.config.base_dn = None
    mulithost.<host_by_role>.config.dns_fowarder = 8.8.8.8
    multihost.domain.type = ipa
    multihost.domain.name = <name from plugin cfg file>
    multihost.domain.hosts = [] list of hosts from plugin cfg file
    multihost.domain.realm = uppercase of name
    multihost.domain.basedn = dc=parts,dc=of,dc=name

- Run a command remotely::

    class TestClass:
        def test_case_1(self, multihost):
            multihost.master.run_command(['echo', 'run'])

- Run a command remotely that needs shell functionality::

    class TestClass:
        def test_case_2(self, multihost):
            multihost.master.run_command('echo run|grep run')

- Run a command and check results::

    class TestClass:
        def test_case_3(self, multihost):
            expected_out = "admin"
            multihost.master.qerun(['ipa', 'user-find', 'admin'],
                                    exp_returncode=0,
                                    exp_output=expected_out)
    
- Check if file exists on remote host::

    class TestClass:
        def test_case_3(self, multihost):
            file_name = '/tmp/check_file'
            if multihost.client.transport.file_exists(file_name):
                print "FILE FOUND"
            else:
                print "FILE NOT FOUND"

- Read file on remote host to a variable::

    class TestClass:
        def test_case_3(self, multihost):
            file_name = '/tmp/check_file'
            contents = multihost.client.get_file_contents(file_name)

- Put variable contents to file on remote host::

    class TestClass:
        def test_case_3(self, multihost):
            file_name = '/tmp/check_file'
            contents = "This is a test\nNot a good one\nBut a test anyway."
            multihost.client.put_file_contents(file_name, contents)

- creating a support library function to use multihost::

    def my_user_check(host, username):
        cmd = host.run_command(['ipa', 'user-show', username], raiseonerr=False)
        if username in cmd.stdout_text:
            print "USER FOUND"
        else:
            print "USER NOT FOUND"
