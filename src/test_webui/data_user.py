ENTITY = 'user'
PKEY = 'itest-user'
DATA = {
    'pkey': PKEY,
    'add': [
        ('textbox', 'uid', PKEY),
        ('textbox', 'givenname', 'FirstName'),
        ('textbox', 'sn', 'LastName'),
    ],
}
