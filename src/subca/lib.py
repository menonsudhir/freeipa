"""
IPA Lightweight Sub CA helper function
"""


def check_ca_output(subca, output):
    """
    Helper function to check common output for Sub
    CA find and add
    """
    name = subca.get('name', None)
    description = subca.get('description', None)
    cname = subca.get('cname', name)
    realm = subca.get('realm', None)

    assert "Name: {0}".format(name) in output
    if description:
        assert "Description: {0}".format(description) in output
    if realm:
        assert "Subject DN: " \
               "CN={0},O={1}".format(cname, realm) in output
    assert "Issuer DN: CN=Certificate " \
           "Authority,O={0}".format(subca['realm']) in output


def check_ca_add_output(subca, output):
    """
    Helper function for Sub CA add output checking
    """
    assert "Created CA \"{0}\"".format(subca['name']) in output
    check_ca_output(subca, output)


def check_ca_find_output(subca, output):
    """
    Helper function for Sub CA find output checking
    """
    check_ca_output(subca, output)
    assert "Number of entries returned 1" in output


def check_ca_show_output(subca, output):
    """
    Helper function for Sub CA show output checking
    """
    subca_name = subca.get('name', 'ipa')
    subca_desc = subca.get('description', subca_name)
    subca_cname = subca.get('cname', subca_name)
    assert "Name: {0}".format(subca_name) in output
    assert "Description: {0}".format(subca_desc) in output
    assert "Subject DN: " \
           "CN={0},O={1}".format(subca_cname,
                                 subca['realm']) in output
    assert "Issuer DN: CN=Certificate " \
           "Authority,O={0}".format(subca['realm']) in output


def check_ca_del_output(subca, output):
    """
    Helper function for Sub CA del output checking
    """
    assert "Deleted CA \"{0}\"".format(subca['name']) in output
