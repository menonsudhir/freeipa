"""
This is a quick test for CA Cert Renewal scenarios
"""
import pytest
from ipa_pytests.qe_class import multihost
from ipa_pytests.qe_install import setup_master, uninstall_server
from ipa_pytests.ca_cert_renewal.lib_ca_renewal import renew_certs


class TestAutoRenewCert(object):
    """ Test Class """
    def class_setup(self, multihost):
        """ Setup for class """
        multihost.realm = multihost.master.domain.realm

        print("Using following hosts for CA Cert Renewal testcases")
        print("*" * 80)
        print("MASTER: %s" % multihost.master.hostname)
        print("*" * 80)

    def test_auto_renew_cert(self, multihost):
        """ Test for auto renew cert """
        # cleanup if server is alrady installed
        uninstall_server(multihost.master)

        # install master
        setup_master(multihost.master)

        try:
            # perform renewal
            renewcert_data = renew_certs(multihost.master)

            # renewcert_data[0] = resubmit, renewcert_data[1] = current date
            # will need to remove if-else block when bz-1660877 get fix
            if renewcert_data[0] != 0 and renewcert_data[1] > 2145916800:
                pytest.xfail("Known issue bz-1660877")
            else:
                pytest.fail("Failed: Seems like bz-1660877 fixed or some other issue occured!!")

        finally:
            # cleanup
            uninstall_server(multihost.master)

    def class_teardown(self, multihost):
        """ Teardown for class """
        print("Class teardown for CA Cert Renewal")
