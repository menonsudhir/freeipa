Layout
======

This doc provides information about the layout of the IdM QE IPA Tests
project dir and test suites.

Package
-------

- idm_qe_ipa_tests/
    - This is the project package directory containing setup for installing
      the package.
- idm_qe_ipa_tests/pylint.cfg
    - project's pylint config.  This supports the style needed for the IdM
      tests.
- idm_qe_ipa_tests/mh_cfg.yaml
    - example multihost config
- idm_qe_ipa_tests/setup.py
    - main package setup file
- idm_qe_ipa_tests/idm_qe_ipa_tests/
    - This is the main root directory for the project.  It contains all 
      test suites and necessary support libraries

Root
----

- qe_class.py
    - This is the main framework interface class.  It provides an extension
      of the pytest multihost plugin.  This extension provides additional 
      variables and functions used by test suites.
    - More information on qe_class can be found here:
      :doc: `qeclass`
- qe_install.py
    - This is a basic installer for use by most test cases.  It provides
      functions for installing IPA Master, Replicas, and Clients.
    - setup_master(master)
        - master is multihost.master object/instance
    - setup_replica(replica, master)
        - replica is multihost.replica object/instance
        - master is multihost.master object/instance
    - setup_client(client, master)
        - client is multihost.client object/instance
        - master is multihost.master object/instance
- shared/
    - This is a main location for adding shared functions.
- <test_suite>/
    - dir for each test suite

Test Dir
--------

- conftest.py
    - This is the environment test configuration file.  It defines the fixtures
      necessary to interface with the multihost plugin for the test.
    - This includes defining the environment hosts with make_multihost_fixture
    - This also includes any required session scoped setup/teardown fixtures.
    - more information can be found here:
      :doc: `conftest`
- pytest.ini
    - This is the default config per test for running pytest command.
    - This helps with running individual tests if different args required
- test_<case or casegroup>.py
    - this is the test case module.  It can include either a single case or 
      multiple via a group of test cases.
