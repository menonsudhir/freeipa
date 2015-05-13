Multihost config
================

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
