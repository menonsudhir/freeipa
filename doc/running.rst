Running test suites
===================

Picking a config
----------------

To run the tests, you have to pick a multihost config template to use.
These files are located in the ipa-pytests/config directory.  They are
named based on the topology they represent.  The naming scheme is
mh_cfg_<topology_code>.yaml:

- m = master
- r = replica
- c = client
- o = other
- mrc = topo with master, replica, and client
- mrr = topo with master and two replicas

Using a pre-defined config
--------------------------

- Setup the Multihost Config for the test you need to run::

    export EXISTING_NODES="<space separated list of FQDN's or IP's>"
    cd ~/ipa-pytests
    cp config/mh_cfg_mrc.yaml mh_cfg.yaml
    NUM=0
    for HOST in $EXISTING_NODES; do
        NUM=$(( NUM += 1 ))
        sed -i "s/hostname$NUM/$HOST/" mh_cfg.yaml
    done

- For more information on Setting up the multihost config::

:doc: `multihost`

Executing tests
---------------

To execute tests, you can execute a suite, a sub-suite (module), or
an individual test case.  In most cases, test cases should be written
so that they can be executed independently.  However, some cases are
difficult to do that as they rely on previous cases.  So, it may be
that some require running a sub-suite or full suite to execute properly.

Note that if you are running in an isolated environment, you may not be
able to use /root/multihost_tests/ on the test Runner.

- Run test suite::

    cd ipa-pytests
    py.test --junit-xml=/root/multihost_tests/junit.xml \
            --multihost-config=mh_cfg.yaml -v \
            src/<test_suite_dir>

- Run individual test sub-suite (module)::

    cd ~/ipa-pytests
    py.test --junit-xml=/root/multihost_tests/junit.xml \
            --multihost-config=mh_cfg.yaml -v \
            src/<test_suite_dir>/<test_module>.py

- Run individual test case::
    
    cd ~/ipa-pytests
    py.test --junit-xml=/root/multihost_tests/junit.xml \
            --multihost-config=mh_cfg.yaml -v \
            src/<test_suite_dir>/<test_module>.py::<TestClass>::<test_case>

- Example 1 -- run functional services full suite::

    cd ~/ipa-pytests
    py.test --junit-xml=/root/multihost_tests/junit.xml \
            --multihost-config=mh_cfg.yaml -v \
            src/functional_services

- Example 2 -- run functional services env setup and http tests::
    
    cd ~/ipa-pytests
    py.test --junit-xml=/root/multihost_tests/junit-setup_env.xml \
            --multihost-config=mh_cfg.yaml -v \
            src/functional_services/test_0001_setup_env.py

    py.test --junit-xml=/root/multihost_tests/junit-setup_http.xml \
            --multihost-config=mh_cfg.yaml -v \
            src/functional_services/test_0002_setup_http.py

    py.test --junit-xml=/root/multihost_tests/junit-http_tests.xml \
            --multihost-config=mh_cfg.yaml -v \
            src/functional_services/test_0003_http_tests.py


