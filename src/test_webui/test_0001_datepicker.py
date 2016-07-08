"""
This is a testsuite for Datepicker ref
"""
import pytest
from ipa_pytests.qe_class import multihost
from ipa_pytests.shared.user_utils import add_ipa_user
from ipa_pytests.shared.utils import service_control
from ui_lib import ui_driver
import data_user as user


class TestDatePicker(object):
    """ Test Class """
    def class_setup(self, multihost):
        """ Setup for class """
        print("Using Master: %s \n" % multihost.master.hostname)
        multihost.krb5key = 'krbprincipalexpiration'

    def test_0001_krb5_principal_set_date(self, multihost):
        """
        Set valid date in Kerberos Principal Expiration Date
        """
        multihost.driver.init_app()
        multihost.driver.add_record(user.ENTITY, user.DATA)
        multihost.driver.navigate_to_record(user.PKEY)
        multihost.driver.fill_fields([('textbox',
                                       multihost.krb5key,
                                       '2016-12-12')])
        multihost.driver.wait_for_request(n=10)
        multihost.driver.facet_button_click('save')
        multihost.driver.assert_no_error_dialog()
        multihost.driver.logout()

    def test_0002_krb5_principal_set_invalid_date_spl_chr(self, multihost):
        """
        Set Invalid date with special characters in Kerberos Principal
        Expiration Date
        """
        multihost.driver.init_app()
        multihost.driver.add_record(user.ENTITY, user.DATA)
        multihost.driver.navigate_to_record(user.PKEY)
        multihost.driver.fill_fields([('textbox',
                                       multihost.krb5key,
                                       'x16-12-12')])
        multihost.driver.wait_for_request(n=10)
        multihost.driver.assert_button_enabled('save', enabled=False)
        multihost.driver.logout()

    def test_0003_krb5_principal_set_invalid_date_from_past(self, multihost):
        """
        Set invalid date from past in Kerberos Principal
        Expiration Date
        """
        multihost.driver.init_app()
        multihost.driver.add_record(user.ENTITY, user.DATA)
        multihost.driver.navigate_to_record(user.PKEY)
        multihost.driver.fill_fields([('textbox',
                                       multihost.krb5key,
                                       '1016-12-12')])
        multihost.driver.wait_for_request(n=10)
        multihost.driver.facet_button_click('save')
        multihost.driver.assert_no_error_dialog()
        multihost.driver.logout()

    def test_0004_otp_token_set_valid_date(self, multihost):
        """
        Set a valid date in OTP token
        """
        multihost.driver.init_app()
        multihost.driver.add_record(user.ENTITY, user.DATA)
        multihost.driver.navigate_to_record(user.PKEY)
        multihost.driver.action_list_action('add_otptoken', False)
        multihost.driver.assert_dialog()
        multihost.driver.fill_fields([('textbox',
                                       'ipatokennotbefore',
                                       '2016-1-1')])
        multihost.driver.fill_fields([('textbox',
                                       'ipatokennotafter',
                                       '2016-12-12')])
        multihost.driver.dialog_button_click('add')
        multihost.driver.assert_dialog()
        multihost.driver.dialog_button_click('ok')

    def class_teardown(self, multihost):
        """ Teardown for class """
        print("teardown for test_webui")
