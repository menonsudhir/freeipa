"""
Shared support for ipa host control
- host_mod - to modify service options
"""

import paths

def host_mod(host, hostname, options=None, raiseonerr=True):
    """
    Helper function to modify service
    :param host: multihost
    :param hostname: hostname
    :param options: options without --
    """
    if not options:
        options = {}
    cmd = [paths.IPA, 'host-mod']
    for key, value in options.iteritems():
        key = "--" + key
        if isinstance(value, (tuple, list)):
            for item in value:
                cmd.extend((key, item))
        else:
            cmd.extend((key, value))
    cmd.append(hostname)
    run = host.run_command(cmd, raiseonerr=raiseonerr)
    return run
