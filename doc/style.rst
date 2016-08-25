Style Guide
===========

This is the IPA PyTests style guide.

Test Suite Directories
----------------------

- Name:
    - Use a simple name, all lower case, words separated by underscores.
    - Name should describe what is being tested.

- Contents:
    - config/ directory to contain config or data files to install in
      /opt/ipa_pytests/<test_suite>
    - conftest.py file to define configuration for multihost plugin as
      well as session setup and teardown requirements
    - __init__.py empty file needed for pytests and python packaging.
    - pytest.ini file to define common pytest args for this suite.
    - test suite module files

Test Suite Modules (aka Sub-Suites)
-----------------------------------

- Name:
    - test_<number>_<sub_suite_name>.py
        - number is used here to sort by expected execution order.  even
          if order does not matter.
        - sub_suite_name should be simple name, all lower case, words 
          separated by underscores.
        - sub_suite_name should describe what is being tested.

- Contents:
    - module docstring
    - library/module imports
    - May contain support functions if used only by this module
    - Test Class

Test Classes
------------

- Name:
    - TestSomeThing
    - Use name describing the tests.
    - Name should have no word separated and be camel case
    - This is default expectation of pytest.

- Contents:
    - class_setup
    - test cases
    - class_teardown

Test Cases
----------

- Name:
    - test_<number>_<test_description>
        - number is used here to sort by expected execution order.  even
          if order does not matter.
        - test_description here is to make sure we can tell what is tested.
        - test_description should be simple, lower case, words separated
          by underscores.

- Contents:
    - include docstring describing test
    - each test case should be as small as possible.
    - test case should provide test code only.
    - there should be one test case per method
    - test cases should be defined by the test plan
    - setup code should be run in setup method or session setup
    - test cases should not do their own setup
    - test cases should be tagged with pytest markers.  See
      :doc:`markers`

Test Setup and Teardown
-----------------------

- Name:
    - session setup - <suite>.conftest.TestPrep.setup
    - session teardown - <suite>.conftest.TestPrep.teardown
    - class setup - <suite>.<module>.<class>.class_setup
    - class teardown - <suite>.<module>.<class>.class_teardown

- Setup Contents:
    - Setup constitutes any action necessary to prepare for a test
    - Setup typically includes IPA install, user/group creation, etc.
    - Setup can be run per session or per class.
    - Setup code should be separated from test cases and run from
      session or class setup.

- Teardown Contents:
    - Teardown constitutes any action necessary to clean up after
      a test or tests.
    - Teardown typically includes user/group removal, IPA uninstall, etc.
    - Teardown should undo everything that both setup and the test case(s)
      did to the system.
    - An ideal teardown would leave the system in the state before the
      test was run (pre-setup).
    - Teardown may be considered optional if the suite is to be used in
      conjunction with other test suites (e.g. an upgrade test might opt
      out of teardown so user tests could be run afterwards).

General Style and Standards
---------------------------

- max line length 120
- use spaces, not tabs for indentation
- use 4 spaces per indentation level

