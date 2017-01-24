"""
DNS related functions
"""


def dns_record_add(host, zone=None, rec_name=None, rec_type=None, rec_ip=[]):
    """
    Helper function to add DNS record
    :param host: Hostname
    :param zone: Zone Name to which host needs to be added
    :param rec_name: Record Name
    :param rec_type: Record Type (e.g., A, AAAA)
    :param rec_ip: Record IP Address
    """
    if any(x is None for x in [host, zone, rec_name, rec_type]):
        return

    cmd = ['ipa', 'dnsrecord-add']
    cmd.append(zone)
    cmd.append(rec_name)
    if rec_type == 'A' and rec_ip:
        if len(rec_ip) > 1:
            rec_ips = ",".join(rec_ip)
        else:
            rec_ips = rec_ip[0]

        cmd.append('--a-rec={0}'.format(rec_ips))

    print("Executing : [{0}]".format(" ".join(cmd)))
    return host.run_command(cmd, raiseonerr=0)
