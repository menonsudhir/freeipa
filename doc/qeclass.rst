QE Class
========

This is the extension to the multihost plugin for IPA PyTest.  It provides
additional variables and functions used by IdM QE IPA Tests.

QeConfig
--------

Adds new config variables needed for tests.

- admin_id - IPA Admin principal ID
- admin_pw - IPA Admin password
- dirman_id - IPA Directory Server Manager ID
- dirman_pw - IPA Directory Server Manager password
- dns_forwarder - DNS forwarder for cases where DNS is setup

QeDomain
--------

Adds domain specific variables for tests.

- realm - IPA REALM
- basedn - IPA Directory Server Base DN suffix

QeHost
------

This is the main shared library class.  This provides the most widely used
functions needed by all hosts in the environmet.

- run_hostname
    - example function for how to add new shared method/function
- kinit_as_user
    - kinit as a user with password provided
- kinit_as_admin
    - kinit as admin_id with admin_pw
- qerun
    - run command with stdin and check return code and output
- yum_install
    - install software


multihost
---------

This fixture defines the multihost plugin config.  It defines a minimum of 1 IPA
Master.  The number of IPA Replicas, Clients, or Other should be defined in
conftest.py.

test_count
----------

This is a fixture to define a default variable TEST_COUNT that increments with
every new test case function executed.

qe_use_class_setup
------------------

This fixture defines class_setup and class_teardown class method defaults that will
be executed during the class setup and teardown phases.

mark_test_start
---------------

This is an output formatting fixture.  It simply wraps the start and end of a
test execution.

pytest_runtest_makereport
-------------------------

This is a pytest hook that is currently written to define some logging requirements.
This function should be calling log_test_phase_results to write out log results.
For our logging requirements, we want to still see a skipped status for the "call"
phase.  So a specific log entry is created when these are "skipped" due to the setup
phase failing.

log_test_phase_results
----------------------

This is a function to log to logstash.  It simply logs the results of a test phase.
