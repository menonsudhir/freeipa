"""
IPA Lightweight Sub CA helper class
"""


def ca_add(host, subca):
    """
    Helper function to add Sub CA
    """
    subca_name = subca.get('name', 'subca')
    subca_desc = subca.get('description', subca_name)
    subca_cname = subca.get('cname', subca_name)
    subca_realm = subca.get('realm', None)

    if not subca_realm:
        return (1, '', 'SubCA Subject missing')

    cmd = "ipa ca-add {0} " \
          "--desc \"{1}\" " \
          "--subject \"CN={2},O={3}\"".format(subca_name,
                                            subca_desc,
                                            subca_cname,
                                            subca_realm)
    return local_run_cmd(host, cmd)

def ca_find(host, subca):
    """
    Helper function to find Sub CA
    """
    subca_name = subca.get('name', 'subca')

    cmd = "ipa ca-find {0}".format(subca_name)
    return local_run_cmd(host, cmd)

def ca_del(host, subca):
    """
    Helper function to delete Sub CA
    """
    subca_name = subca.get('name', 'subca')
    cmd = "ipa ca-del {0}".format(subca_name)
    return local_run_cmd(host, cmd)

def ca_show(host, subca):
    """
    Helper function to show Sub CA
    """
    subca_name = subca.get('name', 'subca')
    cmd = "ipa ca-show {0}".format(subca_name)
    return local_run_cmd(host, cmd)

def ca_acl_find(host, subca_acl):
    """
    Helper function to find Sub CA ACL
    """
    subca_acl_name = subca_acl.get('name', 'hosts_services_caIPAserviceCert')
    cmd = "ipa caacl-find {0}".format(subca_acl_name)
    return local_run_cmd(host, cmd)

def ca_acl_add_ca(host, subca):
    """
    Helper function to add Sub CA in ACL
    """
    subca_acl_name = subca.get('name', 'hosts_services_caIPAserviceCert')
    subca_acl_ca = subca.get('subca', 'ipa')
    cmd = "ipa caacl-add-ca {0} --cas={1}".format(subca_acl_name, subca_acl_ca)
    return local_run_cmd(host, cmd)

def local_run_cmd(host, cmd, raiseonerr=False):
    """
    Local run command
    """
    print("Running : {0}".format(cmd))
    cmdout = host.run_command(cmd, raiseonerr=False)
    return (cmdout.returncode, cmdout.stdout_text, cmdout.stderr_text)
