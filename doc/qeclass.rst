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
