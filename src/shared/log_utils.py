"""
log_utils - provide functions to help with capturing and gathering logs and log info
"""

import re
from ipa_pytests.shared import paths


def backup_logs(host, logfiles):
    """ backup log files to a common, known tar.gz file """
    tarball = '/root/idm-sosreport.tar'
    targz = tarball + '.gz'
    if host.transport.file_exists(targz):
        host.run_command([paths.GUNZIP, targz])
    for logfile in logfiles:
        if not host.transport.file_exists(logfile):
            continue
        stripped_name = re.sub('^/', '', logfile)
        host.run_command([paths.TAR, 'f', tarball, '--delete',
                          stripped_name], raiseonerr=False)
        host.run_command([paths.TAR, 'uf', tarball, logfile])
    if host.transport.file_exists(tarball):
        host.run_command([paths.GZIP, tarball])
