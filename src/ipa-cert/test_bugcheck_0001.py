"""
Overview:
TestSuite to verify BZs related to certificates
SetUp Requirements:
-Latest version of RHEL OS
-Need to test for Master
"""
import pytest
import time
from ipa_pytests.qe_class import multihost
from ipa_pytests.shared.user_utils import add_ipa_user
from ipa_pytests.shared.ipa_cert_utils import ipa_cert_request
from ipa_pytests.shared.openssl_utils import openssl_util
from ipa_pytests.shared.qe_certutils import certutil


config_file = "/tmp/openssl.conf"
csr_file = "test.csr"


class TestBugCheck(object):
    """ Test Class """

    def class_setup(self, multihost):
        """
        Setup for class
        """
        print("\nClass Setup")
        print("MASTER: ", multihost.master.hostname)

    def test_0001_bz1254641(self, multihost):
        """
        Test to verify bugzilla 1254641 - Remove CSR allowed-extensions restriction
        :param multihost:
        :return:
        """
        try:
            multihost.master.kinit_as_admin()
            new_user = "alice"
            filedata = "[ req ]\n" \
                       "prompt = no\n" \
                       "distinguished_name = " + new_user + "\n" \
                       "req_extensions = exts\n" \
                       "\n" \
                       "[ " + new_user + " ]\n" \
                       "commonName = "+new_user+"\n" \
                       "\n" \
                       "[ exts ]\n" \
                       "1.2.840.10070.8.1=DER:30:27:30:25:30:04:02:02:00:FF:0C:0A:4F:75:74:73:74:61" \
                       ":74:69:6F:6E:02:02:00:FF:0C:0A:49:45:43:36:32:33:35:31:2D:38:0A:01:03\n"
            add_ipa_user(multihost.master, user=new_user)
            multihost.master.put_file_contents(config_file, filedata)
            arg_list = ['req', '-config', config_file, '-nodes', '-new', '-newkey', 'rsa:2048', '-keyout', 'test.key']
            arg_list.extend(['-out', csr_file])
            openssl_util(multihost.master, arg_list)

            ipa_cert_request(multihost.master, csr_file, add=True, principal=new_user, profile_id='IECUserRoles')
        except StandardError as errval:
            print("Error %s" % (str(errval.args[0])))
            pytest.skip("test_0001_bz1254641")

    def test_0002_bz1351593(self, multihost):
        """
        IDM-IPA-TC: Custom permission for insufficient privileges check in cert revoke
        """
        test_host = 'bz1351593.' + multihost.master.domain.name
        user = "retriever"
        password = multihost.master.config.admin_pw

        multihost.master.kinit_as_admin()
        multihost.master.qerun(['ipa', 'host-add', '--force', test_host])

        cert_db = '/tmp/' + test_host + '.db'
        multihost.master.transport.mkdir(cert_db)
        multihost.master.put_file_contents(cert_db + '/passwd.txt', '')
        csr = "/tmp/" + test_host + '.csr'
        cert = certutil(multihost.master, cert_db)
        subject_base = cert.get_ipa_subject_base(multihost.master)
        subject = "CN=" + test_host + "," + subject_base
        cert.request_cert(subject, csr)

        runcmd = ['ipa', 'cert-request', csr,
                  '--principal=host/' + test_host]
        cmd = multihost.master.run_command(runcmd)
        for line in cmd.stdout_text.split('\n'):
            if "number:" in line:
                cert_serial = line.split(': ')[1]

        runcmd = ['ipa', 'privilege-add', 'GoFetch',
                  '--desc="Can only retrieve Certs"']
        runcmd = ' '.join(runcmd)
        multihost.master.qerun(runcmd)

        runcmd = ['ipa', 'privilege-add-permission', 'GoFetch',
                  '--permissions="Retrieve Certificates from the CA"']
        runcmd = ' '.join(runcmd)
        multihost.master.qerun(runcmd)

        runcmd = ['ipa', 'role-add', 'ITretrievers',
                  '--desc="Guys whose roles are to retrieve certs"']
        runcmd = ' '.join(runcmd)
        multihost.master.qerun(runcmd)

        time.sleep(3)
        runcmd = ['ipa', 'role-add-privilege', 'ITretrievers',
                  '--privileges=GoFetch']
        multihost.master.qerun(runcmd)

        add_ipa_user(multihost.master, user=user)

        runcmd = ['ipa', 'role-add-member', 'ITretrievers',
                  '--users=retriever']
        multihost.master.qerun(runcmd)

        multihost.master.kinit_as_user(user, password)

        runcmd = ['ipa', 'cert-revoke', cert_serial]
        exp_output = "Insufficient access"
        multihost.master.qerun(runcmd, exp_output=exp_output)

        multihost.master.kinit_as_admin()
        multihost.master.qerun(['ipa', 'privilege-del', 'GoFetch'])
        multihost.master.qerun(['ipa', 'role-del', 'ITretrievers'])
        multihost.master.qerun(['ipa', 'host-del', test_host])

    def class_teardown(self, multihost):
        """ Full suite teardown """
        pass
