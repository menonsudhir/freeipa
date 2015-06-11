Markers for Test Cases
======================

Pytest provides a test tagging mechanism called "markers".  We will
use this to categorize our tests in various ways.  This will allow
pytest to run a subset of test cases depending on the marker passed
on the command line.

Marking tests
-------------

- Markers should be set for test case methods.
- Markers are added right above the def line for the method
- Markers should look like--"@pytest.mark.<markername>"
- Example 1 with simple markers::

    import pytest
    class Test_0001:
        @pytest.mark.tier1
        def test_0001(self, multihost):
            print "\n0001"

        @pytest.mark.tier1
        def test_0002(self, multihost):
            print "\n0002"

        @pytest.mark.tier2
        def test_0003(self, multihost):
            print "\n0003"

- Example 2 with more complex markers::

    import pytest
    class TestMarkers:
        @pytest.mark.tier1
        def test_0001(self):
            print "test_0001 tier1 marker"

        @pytest.mark.tier2
        def test_0002(self):
            print "test_0002 tier2 marker"

        @pytest.mark.tier3
        def test_0003(self):
            print "test_0003 tier3 marker"

        @pytest.mark.tier1
        @pytest.mark.regression
        def test_0004(self):
            print "test_0004 tier1 regression"
        
        @pytest.mark.tier1
        @pytest.mark.acceptance
        def test_0005(self):
            print "test_0005 tier1 acceptance"

        @pytest.mark.tier1
        @pytest.mark.functional
        def test_0006(self):
            print "test_0006 tier1 functional"

        @pytest.mark.tier2
        @pytest.mark.regression
        def test_0007(self):
            print "test_0004 tier2 regression"
        
        @pytest.mark.tier2
        @pytest.mark.acceptance
        def test_0008(self):
            print "test_0005 tier2 acceptance"

        @pytest.mark.tier2
        @pytest.mark.functional
        def test_0009(self):
            print "test_0006 tier2 functional"

Running Tests with Markers
--------------------------

- the test cases to run can be listed with '-m <marker>'::
    
    py.test -m tier1
    py.test -m functional
    
- the marker can be defined using basic logic as a quoted string::
    
    py.test -m 'tier1 and functional'
    py.test -m 'tier2 and not acceptance'

Test Tier
---------

Tier markers are used to indicate to which tier level the test case
belongs.  @pytest.mark.tier1, @pytest.mark.tier2, etc.

- Test tier tagging should conform to the standards of the organization.
- tier0 - Unit testing.  test individual bits of source code.
- tier1 - lowest level of functional, acceptance or regression testing.
    - If this fails, testing stops and product sent back to development.
    - Should cover any functionality of the product or feature that
      absolutely must be available.
    - Includes things like installing software, adding users, etc.
- tier2 - main level of functional and integration testing
    - This tier covers more complex functional tests
    - It also includes typical assortments of cli positive and
      negative acceptance tests.  Ones not already covers by tier1.
- tier3 - includes the most complex tests
    - This includes functional tests mimicing actual business use.
    - It also includes system and more complex integration tests.
    - Large scale performance testing falls into this tier.

Test Type
---------

- acceptance -
- regression -
- functional -
- integration -
