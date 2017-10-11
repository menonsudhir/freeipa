"""
ipa cert shared support utility functions
- cert_request
"""
import ipa_pytests.shared.paths as paths


def ipa_cert_request(host, csr_file, add=True, principal=None, profile_id=None, request_type=None):
    """
    Function to submit a certificate signing request
    :param host: hosname
    :param csr_file: string
    :param add: bool - true or false
    :param principal: string
    :param profile_id: string
    :param request_type: string
    :return: None
    """
    cmd_list = ['ipa', 'cert-request', csr_file]
    if add:
        cmd_list.append('--add')
    if request_type is not None:
        cmd_list.extend(['--request-type', request_type])
    if principal is not None:
        cmd_list.extend(['--principal', principal])
    if profile_id is not None:
        cmd_list.extend(['--profile-id', profile_id])
    print("Running : {0}".format(" ".join(cmd_list)))
    host.run_command(cmd_list)


def ipa_cert_show(host, serial, ca=None, out=None):  # pylint: disable=invalid-name
    """
    Show a cert in IPA.
    :param host:  multihost host object
    :param serial: string
    :param ca: string
    :param out: string
    :return: string
    """
    cmd_list = ['ipa', 'cert-show', serial]
    if ca:
        cmd_list.extend(['--ca', ca])
    if out:
        cmd_list.extend(['--out', out])
    print("Running : {0}".format(" ".join(cmd_list)))
    cmd = host.run_command(cmd_list)
    return cmd.stdout_text


def ipa_cert_revoke(host, serial, reason=None, ca=None):  # pylint: disable=invalid-name
    """
    Revoke a cert in IPA.
    :param host:  multihost host object
    :param serial: string
    :param reason: string
    :param ca: string
    :return: None
    """
    cmd_list = ['ipa', 'cert-revoke', serial]
    if reason:
        cmd_list.extend(['--revocation-reason', reason])
    if ca:
        cmd_list.extend(['--ca', ca])
    print("Running : {0}".format(" ".join(cmd_list)))
    host.run_command(cmd_list)


def ipa_cert_remove_hold(host, serial, ca=None):  # pylint: disable=invalid-name
    """
    Remove a revoke hold on a cert in IPA.
    :param host:  multihost host object
    :param serial: string
    :param ca: string
    :return: None
    """
    cmd_list = ['ipa', 'cert-remove-hold', serial]
    if ca:
        cmd_list.extend(['--ca', ca])
    print("Running : {0}".format(" ".join(cmd_list)))
    host.run_command(cmd_list)


def ipa_ca_cert_update(host):
    """
    Update CA cert on given host
    :param host: multihost host object
    """
    cmd_list = [paths.IPACERTUPDATE]
    print("Running : {0}".format(" ".join(cmd_list)))
    return host.run_command(cmd_list, raiseonerr=False)
