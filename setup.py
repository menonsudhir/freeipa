from distutils.core import setup

setup(name='ipa_pytests',
      version='0.1',
      description='IPA Python Tests by IdM QE',
      url='http://git.app.eng.bos.redhat.com/ipa-pytests.git/',
      author='Scott Poore',
      author_email='spoore@redhat.com',
      license='GPL',
      package_dir = {'ipa_pytests': 'src'},
      packages=['ipa_pytests',
                'ipa_pytests.quicktest',
                'ipa_pytests.functional_services',
                'ipa_pytests.shared',
                'ipa_pytests.scripts',
               ],
      data_files=[('/opt/ipa_pytests/functional_services',
                   ['src/functional_services/config/http-krb.conf',
                    'src/functional_services/config/ldap-enablessl.ldif',
                    'src/functional_services/config/ldap-instance.inf',
                    'src/functional_services/config/ldap-loglevel.ldif',
                    'src/functional_services/config/ldap-pwscheme.ldif',
                    'src/functional_services/config/ldap-sasl.ldif',
                    'src/functional_services/config/ldap-user.ldif',
                   ]
                  ),
                  ('/opt/ipa_pytests/',
                   ['config/ipa_pytests_logstash_cfg.yaml',
                   ]
                  ),
                  ('/root/multihost_tests',
                   ['config/multihost_tests/env.sh',
                    'config/multihost_tests/.coveragerc',
                    'config/multihost_tests/sitecustomize-add.py'
                   ]
                  ),
                 ]
     )
