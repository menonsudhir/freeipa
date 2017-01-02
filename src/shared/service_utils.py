"""
Shared support for ipa service control
- service_mod - to modify service options
- service_show - show service info if exist
"""

import paths

def service_mod(host, service, options=None):
    """
    Helper function to modify service
    :param host: multihost
    :param service: servicename
    :param options: options without --
    """
    if not options:
        options = {}
    cmd = [paths.IPA, 'service-mod']
    for key, value in options.iteritems():
        key = "--" + key
        if isinstance(value, (tuple, list)):
            for item in value:
                cmd.extend((key, item))
        else:
            cmd.extend((key, value))
    cmd.append(service)
    run = host.run_command(cmd)
    return run

def service_show(host, service):
    """
    :param host: multihost
    :param service: servicename
    """
    cmd = host.run_command(paths.IPA, 'service-show', service)
    return cmd
