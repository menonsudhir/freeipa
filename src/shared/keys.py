"""
Support library for handling keys used for encryption.
This includes but is not limited to openssl key generation.
"""


def openssl_genrsa(host, key_file_prv, key_file_pub):
    """ helper function to generate 2048bit RSA keypair with openssl """
    if not host.transport.file_exists(key_file_prv):
        host.qerun(['openssl', 'genpkey', '-algorithm', 'RSA', '-out',
                    key_file_prv, '-pkeyopt', 'rsa_keygen_bits:2048'])
    if not host.transport.file_exists(key_file_pub):
        host.qerun(['openssl', 'rsa', '-in', key_file_prv, '-out', key_file_pub,
                    '-pubout'])
