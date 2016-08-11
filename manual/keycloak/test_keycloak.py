""" Keycloak Tests """


class TestKeyCloakSaml(object):
    """ SAML Tests """
    def test_keycloak_saml_0001(self):
        """
        @Title: IDM-IPA-TC: Keycloak: SAML with IPA user via LDAP without kerberos
        @Description:
        @casecomponent: ipa

        @setup:
        1. Install IdM
        2. Install Keycloak on different server
        3. Configure Keycloak to use IdM over LDAP
        4. Create a service provider to test SAML based SSO

        @steps:
        1. Access an SP with LDAP authentication
        2. Access an SP with OTP authentication
        3. Logout from Keycloak

        @expectedresults:
        1. pass LDAP auth with keycloak and be redirected to access SP
        2. pass OTP auth with keycloak and be redirected to access SP
        3. logout from SP as well
        """

    def test_keycloak_saml_0002(self):
        """
        @Title: IDM-IPA-TC: Keycloak: SAML with IPA user via LDAP with kerberos
        @Description:
        @casecomponent: ipa

        @setup:
        1. Install IdM
        2. Install Keycloak on different server
        3. Configure Keycloak to use IdM over LDAP
        4. Configure Keycloak as a Kerberos service in IdM domain following docs
        5. Create a service provider to test SAML based SSO

        @steps:
        1. Kinit on test client with browser
        2. Access an SP with valid Kerberos ticket

        @expectedresults:
        1. get kerberos ticket for IPA user
        2. pass login with kerberos authentication with keycloak to access SP
        """

    def test_keycloak_saml_0003(self):
        """
        @Title: IDM-IPA-TC: Keycloak: SAML with IPA AD Trust user via LDAP without kerberos
        @Description:
        @casecomponent: ipa

        @setup:
        1. Install IdM
        2. Install AD and configure AD Trust
        3. Install Keycloak on different server
        4. Configure Keycloak to use IdM over LDAP
        5. Create a service provider to test SAML based SSO

        @steps:
        1. Access an SP with LDAP authentication of AD user
        2. Access an SP with OTP authentication of AD user
        3. Logout from Keycloak

        @expectedresults:
        1. pass LDAP auth with keycloak and be redirected to access SP
        2. pass OTP auth with keycloak and be redirected to access SP
        3. logout from SP as well
        """

    def test_keycloak_saml_0004(self):
        """
        @Title: IDM-IPA-TC: Keycloak: SAML with IPA AD Trust user via LDAP with kerberos
        @Description:
        @casecomponent: ipa

        @setup:
        1. Install IdM
        2. Install AD and configure AD Trust
        3. Install Keycloak on different server
        4. Configure Keycloak to use IdM over LDAP
        5. Configure Keycloak as a Kerberos service in IdM domain following docs
        6. Create a service provider to test SAML based SSO

        @steps:
        1. Kinit as AD user on test client with browser
        2. Access an SP with valid Kerberos ticket of AD user

        @expectedresults:
        1. get kerberos ticket for AD user
        2. pass login with kerberos authentication with keycloak to access SP
        """


class TestKeyCloakOidc(object):
    """ OpenID Connect tests """
    def test_keycloak_oidc_0001(self):
        """
        @Title: IDM-IPA-TC: Keycloak: OIDC with IPA user via LDAP without kerberos
        @Description:
        @casecomponent: ipa

        @setup:
        1. Install IdM
        2. Install Keycloak on IdM server
        3. Configure Keycloak to use IdM over LDAP
        4. Create a service provider to test OIDC based SSO

        @steps:
        1. Access an SP with LDAP authentication
        2. Access an SP with OTP authentication
        3. Logout from Keycloak

        @expectedresults:
        1. pass LDAP auth with keycloak and be redirected to access SP
        2. pass OTP auth with keycloak and be redirected to access SP
        3. logout from SP as well
        """

    def test_keycloak_oidc_0002(self):
        """
        @Title: IDM-IPA-TC: Keycloak: OIDC with IPA user via LDAP with kerberos
        @Description:
        @casecomponent: ipa

        @setup:
        1. Install IdM
        2. Install Keycloak on IdM server
        3. Configure Keycloak to use IdM over LDAP
        4. Configure Keycloak as a Kerberos service in IdM domain following docs
        5. Create a service provider to test OIDC based SSO

        @steps:
        1. Kinit on test client with browser
        2. Access an SP with valid Kerberos ticket

        @expectedresults:
        1. get kerberos ticket for IPA user
        2. pass login with kerberos authentication with keycloak to access SP
        """

    def test_keycloak_oidc_0003(self):
        """
        @Title: IDM-IPA-TC: Keycloak: OIDC with IPA AD Trust user via LDAP without kerberos
        @Description:
        @casecomponent: ipa

        @setup:
        1. Install IdM
        2. Install AD and configure AD Trust
        3. Install Keycloak on IdM server
        4. Configure Keycloak to use IdM over LDAP
        5. Create a service provider to test OIDC based SSO

        @steps:
        1. Access an SP with LDAP authentication of AD user
        2. Access an SP with OTP authentication of AD user
        3. Logout from Keycloak

        @expectedresults:
        1. pass LDAP auth with keycloak and be redirected to access SP
        2. pass OTP auth with keycloak and be redirected to access SP
        3. logout from SP as well
        """

    def test_keycloak_oidc_0004(self):
        """
        @Title: IDM-IPA-TC: Keycloak: OIDC with IPA AD Trust user via LDAP with kerberos
        @Description:
        @casecomponent: ipa

        @setup:
        1. Install IdM
        2. Install AD and configure AD Trust
        3. Install Keycloak on IdM server
        4. Configure Keycloak to use IdM over LDAP
        5. Configure Keycloak as a Kerberos service in IdM domain following docs
        6. Create a service provider to test OIDC based SSO

        @steps:
        1. Kinit as AD user on test client with browser
        2. Access an SP with valid Kerberos ticket of AD user

        @expectedresults:
        1. get kerberos ticket for AD user
        2. pass login with kerberos authentication with keycloak to access SP
        """
