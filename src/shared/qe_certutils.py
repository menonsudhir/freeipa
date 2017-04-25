"""
Support library of certutils related functionality
This should provide us with functions to perform same actions
we need from certutil commands
"""

import random
import string
from ipa_pytests.shared.utils import rand_str_generator


class certutil(object):
    """
    certutil class to provide functions for similar functionality
    to certutil command
    """
    def __init__(self, host, db_dir):
        """
        Main init for certutil class.
        - Sets up and creates nssdb for certutil commands to use.
        - creates default password and noise files
        """
        self.host = host
        self.db_dir = db_dir
        self.db_password = ""
        self.db_noise = ""
        self.password_file = self.db_dir + "/passwd.txt"
        self.noise_file = self.db_dir + "/noise.txt"
        self.root_key_id = "0x{0}".format(rand_str_generator(20, "0123456789abcdef"))
        self.ipa_ca_key_id = "0x{0}".format(rand_str_generator(20, "0123456789abcdef"))

        if not self.host.transport.file_exists(self.db_dir):
            self.host.transport.mkdir_recursive(self.db_dir)

        if not self.host.transport.file_exists(self.password_file):
            self.db_password = ''.join([random.choice(string.ascii_letters +
                                                      string.digits)
                                        for _ in xrange(32)])
            self.host.put_file_contents(self.password_file, self.db_password)

        if not self.host.transport.file_exists(self.noise_file):
            self.db_noise = ''.join([random.choice(string.ascii_letters +
                                                   string.digits)
                                     for _ in xrange(32)])
            self.host.put_file_contents(self.noise_file, self.db_noise)

        self.host.run_command(['certutil',
                               '-d', self.db_dir,
                               '-N',
                               '-f', self.password_file])

    def add_cert(self, cert_file, nick, trust):
        """ certutil add (-A) command """
        self.host.run_command(['certutil',
                               '-d', self.db_dir,
                               '-A',
                               '-n', nick,
                               '-t', trust,
                               '-a',
                               '-i', cert_file])

    def list_certs(self, nick=None):
        """ certutil list (-L) command """
        cmdstr = ['certutil', '-d', self.db_dir, '-L']
        if nick:
            cmdstr = cmdstr + ['-n', nick]
        cmd = self.host.run_command(cmdstr)
        return cmd.stdout_text, cmd.stderr_text

    def verify_cert(self, nick):
        """ certutil verify (-V) command """
        cmdstr = ['certutil', '-d', self.db_dir, '-V', '-n', nick, '-u', 'ALV']
        cmd = self.host.run_command(cmdstr)
        return cmd.stdout_text.find("certificate is valid")

    def request_cert(self, subject, outfile=None):
        """ certutil request (-R) command """
        cmdstr = ['certutil', '-d', self.db_dir, '-R', '-s', subject,
                  '-a', '-z', self.noise_file]
        if outfile:
            cmdstr = cmdstr + ['-o', outfile]

        cmd = self.host.run_command(cmdstr)
        return cmd.stdout_text, cmd.stderr_text

    def selfsign_cert(self, subject, nick, options=None):
        """ certutil create self-signed cert and add to nssdb (-S) command """
        stdin_text = 'y\n10\ny\n'
        cmdstr = ['certutil',
                  '-d', self.db_dir,
                  '-S',
                  '-n', nick,
                  '-s', subject,
                  '-x',
                  '-t', 'CTu,Cu,Cu',
                  '-g', '2048',
                  '-v', '60',
                  '-z', self.noise_file,
                  '-2',
                  '--keyUsage', 'certSigning,digitalSignature,nonRepudiation',
                  '--nsCertType', 'sslCA,smimeCA,objectSigningCA',
                  '-f', self.password_file]

        if options:
            cmdstr = cmdstr + options

        if "--extSKID" in options:
            stdin_text += '%s\nn\n' % self.root_key_id
        print("\nRunning command : %s with %s as stdin_text" % (" ".join(cmdstr), stdin_text))
        cmd = self.host.run_command(cmdstr, stdin_text=stdin_text, raiseonerr=False)
        return cmd.stdout_text, cmd.stderr_text

    def create_server_cert(self, subject, nick, ca_nick='ca', options=None):
        """ certutil create CA-signed server cert
        and add to nssdb (-S) command """
        cmdstr = ['certutil',
                  '-d', self.db_dir,
                  '-S',
                  '-n', nick,
                  '-s', subject,
                  '-t', ',,',
                  '-z', self.noise_file,
                  '-c', ca_nick,
                  '-f', self.password_file]

        if options:
            cmdstr = cmdstr + options

        print("\nRunning command : %s" % " ".join(cmdstr))
        cmd = self.host.run_command(cmdstr, stdin_text='n\n0\ny\n', raiseonerr=False)
        return cmd.stdout_text, cmd.stderr_text

    def get_ipa_subject_base(self, master):
        """ Get IPA Subject Base from IPA Master """
        suffix = ""
        master.kinit_as_admin()
        cmd = master.run_command(['ipa', 'config-show', '--raw'])
        for line in cmd.stdout_text.split('\n'):
            if "ipacertificatesubjectbase" in line:
                suffix = line.split()[1]
        if suffix == "":
            suffix = "O=" + master.domain.realm
        return suffix

    def export_cert(self, nick, outfile=None):
        """ certutil export command """
        cmdstr = ['certutil',
                  '-d', self.db_dir,
                  '-L',
                  '-n', nick,
                  '-a']
        if outfile:
            cmdstr = cmdstr + ['-o', outfile]
        print("Running: {0}".format(" ".join(cmdstr)))
        cmd = self.host.run_command(cmdstr)
        return cmd.stdout_text, cmd.stderr_text

    def sign_csr(self, csr_in, csr_out, nick, options=None):
        """ Sign given CSR file using nssdb """
        stdin_text = "y\n\ny\n"
        cmdstr = ['certutil',
                  '-C',
                  '-d', self.db_dir,
                  '-i', csr_in,
                  '-o', csr_out,
                  '-c', nick,
                  '-1', '-2',
                  '-z', self.noise_file,
                  '--keyUsage', 'certSigning,digitalSignature,nonRepudiation',
                  '--nsCertType', 'sslCA,smimeCA,objectSigningCA',
                  '-f', self.password_file]
        if options:
            cmdstr += options
        if '--extSKID' in options:
            stdin_text += "%s\n\n\nn\n%s\nn\n" % (self.root_key_id, self.ipa_ca_key_id)

        print("Running: [%s] with stdin_text %s" % (" ".join(cmdstr), stdin_text))
        cmd = self.host.run_command(cmdstr, stdin_text=stdin_text, raiseonerr=False)
        return cmd.stdout_text, cmd.stderr_text
