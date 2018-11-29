"""
Vault tests data file
"""

# pylint: disable=too-many-locals,unused-variable,invalid-name,global-statement

import base64

PREFIX = ''
USER1 = ''
SERVICE1 = ''
PASSWORD = ''
PASS_FILE = ''
PRVKEY_FILE = ''
PUBKEY_FILE = ''
NEW_PRVKEY_FILE = ''
NEW_PUBKEY_FILE = ''
SECRET_VALUE = ''
SECRET_BLOB = ''
SECRET_FILE = ''
SECRET_OUT_FILE = ''
INVALID_KEY = base64.b64encode(b"INIT")
DNE_FILE = ''
LARGE_FILE = ''
DNE_VAULT = []
PRIV_VAULT = []
USER_VAULT = []
SHARED_VAULT = []
SERVICE_VAULT = []


def init(multihost, prefix):
    """ Initialize global variables """
    global PREFIX
    global USER1
    global SERVICE1
    global PASSWORD
    global PASS_FILE
    global PRVKEY_FILE
    global PUBKEY_FILE
    global NEW_PRVKEY_FILE
    global NEW_PUBKEY_FILE
    global SECRET_VALUE
    global SECRET_BLOB
    global SECRET_FILE
    global SECRET_OUT_FILE
    global INVALID_KEY
    global DNE_FILE
    global LARGE_FILE
    global DNE_VAULT
    global PRIV_VAULT
    global USER_VAULT
    global SHARED_VAULT
    global SERVICE_VAULT

    PREFIX = prefix
    USER1 = "testuser1"
    SERVICE1 = "testservice1/" + multihost.master.hostname
    PASSWORD = "Secret123"
    PASS_FILE = "/root/multihost_tests/vault_password.txt"
    PRVKEY_FILE = "/root/multihost_tests/vault_key.prv"
    PUBKEY_FILE = "/root/multihost_tests/vault_key.pub"
    NEW_PRVKEY_FILE = "/root/multihost_tests/new_vault_key.prv"
    NEW_PUBKEY_FILE = "/root/multihost_tests/new_vault_key.pub"
    SECRET_VALUE = "Secret123"
    SECRET_BLOB = "U2VjcmV0MTIzCg=="
    SECRET_FILE = "/root/multihost_tests/vault_secret"
    SECRET_OUT_FILE = "/root/multihost_tests/vault_secret_out"
    INVALID_KEY = base64.b64encode(b"INVALID")
    DNE_FILE = "/root/multihost_tests/dne_file"
    LARGE_FILE = "/root/multihost_tests/large_file"
    DNE_VAULT = ['dne_vault']
    PRIV_VAULT = [PREFIX + '_vault_priv']
    USER_VAULT = [PREFIX + '_vault_user', '--user=' + USER1]
    SHARED_VAULT = [PREFIX + '_vault_shared', '--shared']
    SERVICE_VAULT = [PREFIX + '_vault_service', '--service=' + SERVICE1]
