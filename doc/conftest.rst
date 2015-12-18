Conftest
========

This doc describes the pytest conftest file used to configure fixtures
for using the pytest-multihost plugin.

Define required fixtures and libraries
--------------------------------------

The imports in the conftest.py file at the beginning must include specific
fixtures in order to work properly with this framework.

- Example::

    import pytest
    from ipa_pytests.qe_class import multihost
    from ipa_pytests.qe_class import test_count
    from ipa_pytests.qe_class import mark_test_start
    from ipa_pytests.qe_class import qe_use_class_setup
    from ipa_pytests.qe_class import pytest_runtest_makereport
    from ipa_pytests.shared.utils import add_ipa_user

Set number of host types
------------------------

In conftest.py, you need to set some global variables in the pytest
namespace.  Set the number of replicas, clients, and others in the
pytest_namespace hook.

- Example::

    def pytest_namespace():
        return {'num_replicas': 1,
                'num_clients': 1,
                'num_others': 0}

Session Scoped Setup and Teardown Fixtures
------------------------------------------

This function defines the fixture that sets up the setup and teardown
at the session scope.  This is done by running a TestPrep class method
for each function provided later in this file.

- Example::

    @pytest.fixture(scope="session", autouse=True)
    def setup_session(request, multihost):
        multihost.replica = multihost.replicas[0]
        multihost.client = multihost.clients[0]

        try:
            setup_master(multihost.master)
            setup_replica(multihost.replica, multihost.master)
            setup_client(multihost.client, multihost.master)
        except StandardError as errval:
            print str(errval.args[0])
            pytest.skip("setup_session_skip")

        def teardown_session():
            """ define fixture for session level teardown """
            pass
        request.addfinalizer(teardown_session)

- This is useful for normal test suites to setup env.  It is run by pytest
  for any level of test execution--test suite, sub-suite, or test case.

- This could also pre-create users/groups/hosts/etc used by any/all test
  cases if there are multiple sub-suite test modules.
