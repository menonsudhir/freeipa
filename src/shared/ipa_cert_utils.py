"""
ipa cert shared support utility functions
- cert_request
"""


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
    host.run_command(cmd_list)
