"""
This is a support library that provides functions for IPA specific
Certificates.  Including expiration information as well as general
information about the cert.
"""


class QE_IPA_Certs(object):
    """
    Main IPA Certificate class.  This gets various information on
    IPA Service and CA certificats.
    """
    def __init__(self):
        """ initialize certs instance """
        self.certs = {}
        self.ttls = [2419200, 604800, 259200, 172800, 86400]

    def set_certs(self, certs):
        """ get dict of certificates """
        self.certs = certs

    def get_nicknames(self):
        """ get_nicknames returns list object of nicknames """
        return self.certs.keys()

    def get_soonest_expiration(self):
        """ find the date of the next expiring cert """
        soonest = 0
        for nick in self.certs.keys():
            expiration = int(self.certs[nick]['not-valid-after'])
            if soonest == 0 or soonest > expiration:
                soonest = expiration
        return soonest

    def get_latest_expiration(self):
        """ get latest expiration """
        latest = 0
        for nick in self.certs.keys():
            expiration = int(self.certs[nick]['not-valid-after'])
            if latest == 0 or latest < expiration:
                latest = expiration
        return latest

    def get_resubmit_status(self):
        """ get certificate status """
        for nick in self.certs.keys():
            status = self.certs[nick]['status']
            ca_error = str(self.certs[nick]['ca-error'])
            if ca_error.find("None") == -1:
                return 1
            elif status.find("CA_UNREACHABLE") == 0:
                return 1
            else:
                return 0
