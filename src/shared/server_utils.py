"""
Shared support for ipa server control
"""
import paths


def server_del(host, hostname=None, force=True, raiseonerr=False):
    """
    Helper function to delete server
    :param host: multihost
    :param hostname: server name to delete
    :param force: force delete
    """

    cmdstr = [paths.IPA, 'server-del', hostname]
    if force:
        cmdstr.append('--force')

    print("Executing : [{0}]".format(" ".join(cmdstr)))
    cmd = host.run_command(cmdstr, raiseonerr=raiseonerr)
    return cmd

