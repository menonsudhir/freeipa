"""
Support library of certutils related functionality
This should provide us with functions to perform same actions
we need from certutil commands
"""

import random
import string


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

        if not self.host.transport.file_exists(self.db_dir):
            self.host.transport.mkdir_recursive(self.db_dir)

        if not self.host.transport.file_exists(self.password_file):
            self.db_password = ''.join([random.choice(string.ascii_letters + string.digits)
                                        for _ in xrange(32)])
            self.host.put_file_contents(self.password_file, self.db_password)

        if not self.host.transport.file_exists(self.noise_file):
            self.db_noise = ''.join([random.choice(string.ascii_letters + string.digits)
                                     for _ in xrange(32)])
            self.host.put_file_contents(self.noise_file, self.db_noise)

        self.host.run_command(['certutil', '-d', self.db_dir, '-N', '-f', self.password_file])

    def add_cert(self, cert_file, nick, trust):
        """ certutil add (-A) command """
        self.host.run_command(['certutil', '-d', self.db_dir, '-A', '-n', nick, '-t', trust,
                               '-a', '-i', cert_file])

    def list_certs(self, nick=None):
        """ certutil list (-L) command """
        if nick is None:
            cmd = self.host.run_command(['certutil', '-d', self.db_dir, '-L'])
        else:
            cmd = self.host.run_command(['certutil', '-d', self.db_dir, '-L', '-n', nick])
        return cmd.stdout_text, cmd.stderr_text

    def verify_cert(self, nick):
        """ certutil verify (-V) command """
        cmd = self.host.run_command(['certutil', '-d', self.db_dir, '-V', '-n', nick, '-u', 'ALV'])
        return cmd.stdout_text.find("certificate is valid")

    def request_cert(self, subject, outfile=None):
        """ certutil request (-R) command """
        if outfile is None:
            cmd = self.host.run_command(['certutil', '-d', self.db_dir, '-R', '-s', subject,
                                         '-a', '-z', self.noise_file])
        else:
            cmd = self.host.run_command(['certutil', '-d', self.db_dir, '-R', '-s', subject,
                                         '-a', '-z', self.noise_file, '-o', outfile])
        return cmd.stdout_text, cmd.stderr_text

    def selfsign_cert(self, subject, nick):
        """ certutil create self-signed cert and add to nssdb (-S) command """
        cmd = self.host.run_command(['certutil', '-d', self.db_dir, '-S',
                                     '-n', nick,
                                     '-s', subject,
                                     '-x',
                                     '-t', 'CTu,CTu,CTu',
                                     '-g', '2048',
                                     '-v', '60',
                                     '-z', self.noise_file,
                                     '-2',
                                     '--keyUsage', 'certSigning,digitalSignature,nonRepudiation',
                                     '--nsCertType', 'sslCA,smimeCA,objectSigningCA',
                                     '-f', self.password_file], stdin_text='y\n10\ny\n')
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
