Running test suites
===================

- On Master, setup necessary SSH Keys::

    ssh-keygen -t rsa -N '' -C '' -f ~/.ssh/id_rsa
    cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys
    chmod 600 ~/.ssh/authorized_keys
    ssh-keyscan <MASTER> >> ~/.ssh/known_hosts
    ssh-keyscan <REPLICA> >> ~/.ssh/known_hosts
    ssh-keyscan <CLIENT> >> ~/.ssh/known_hosts
    ssh-copy-id -i ~/.ssh/id_rsa <REPLICA>
    ssh-copy-id -i ~/.ssh/id_rsa <CLIENT>

- On all hosts, setup multihost test dir::

    mkdir -p /root/multihost_tests
    touch /root/multihost_tests/env.sh
    cd /root/multihost_tests

- On Master, if you did not install locally, set PYTHONPATH::

    export PYTHONPATH=/usr/lib/python2.7/site-packages:<path_to_idm_qe_ipa_tests>

- Setup the Multihost Config for the test you need to run::

    cat > mh_cfg.yaml <<EOF
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
    EOF

- For more information on Setting up the multihost config::

:doc: `multihost`

- Run test suite(s)::

    py.test --multihost-config=mh_cfg.yaml -vs idm_qe_ipa_tests/<test_suite_dir>/
