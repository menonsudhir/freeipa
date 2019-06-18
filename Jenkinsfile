@Library('idm-ci')
import idmci.*

env.IDMCI_GITREPO = 'https://gitlab.cee.redhat.com/identity-management/idm-ci.git'
env.IPA_EMAIL = 'ipa-and-samba-team-automation@redhat.com'
env.ANSIBLE_GATHER_TIMEOUT = '60'

node {
        stage("tier-1") {
          parallel(
            "pytest::ipa-hosts": {
                new TeRun([
                    metadata: 'metadata/pytests/ipa-host.yaml',
                    test: 'pytests-ipa-host'
                ]).exec('ipa-slave')
            },
            "pytest::func-svcs": {
                new TeRun([
                    metadata: 'metadata/pytests/functional_services.yaml',
                    test: 'ipa-functional-services',
                ]).exec('ipa-slave')
            },
            "pytest::subca": {
                new TeRun([
                    metadata: 'metadata/pytests/subca.yaml',
                    test: 'ipa-subca',
                ]).exec('ipa-slave')
            },
            "pytest::external-ca": {
                new TeRun([
                    metadata: 'metadata/pytests/external-ca.yaml',
                    test: 'ipa-external-ca',
                ]).exec('ipa-slave')
            },
            "pytest::ca_cert_renewal": {
                new TeRun([
                    metadata: 'metadata/pytests/ca_cert_renewal.yaml',
                    test: 'ca_cert_renewal',
                ]).exec('ipa-slave')
            },
            "pytest::otp": {
                new TeRun([
                    metadata: 'metadata/pytests/otp.yaml',
                    test: 'otp',
                ]).exec('ipa-slave')
            },
            "pytest::vault": {
                new TeRun([
                    metadata: 'metadata/pytests/vault.yaml',
                    test: 'vault',
                ]).exec('ipa-slave')
            },
            "pytest::replica-install": {
                new TeRun([
                    metadata: 'metadata/pytests/replica-install.yaml',
                    test: 'ipa-replica-install',
                ]).exec('ipa-slave')
            },
            "pytest::replica-promotion": {
                new TeRun([
                    metadata: 'metadata/pytests/ipa-replica-promotion.yaml',
                    test: 'ipa-replica-promotion',
                ]).exec('ipa-slave')
            },
            "bash::krbtpolicy": {
                new TeRun([
                    metadata: 'metadata/ipatests/ipa-krbtpolicy.yaml',
                    test: 'ipa-krbtpolicy'
                ]).exec('ipa-slave')
            },
            "bash::dns": {
                new TeRun([
                    metadata: 'metadata/ipatests/ipa-dns.yaml',
                    test: 'ipa-dns'
                ]).exec('ipa-slave')
            },
            "bash::sudo": {
                new TeRun([
                    metadata: 'metadata/ipatests/ipa-sudo.yaml',
                    test: 'ipa-sudo'
                ]).exec('ipa-slave')
            },
            "bash::password": {
                new TeRun([
                    metadata: 'metadata/ipatests/ipa-password.yaml',
                    test: 'ipa-password'
                ]).exec('ipa-slave')
            },
            "bash::cert": {
                new TeRun([
                    metadata: 'metadata/ipatests/ipa-cert.yaml',
                    test: 'ipa-cert'
                ]).exec('ipa-slave')
            },
            "bash::getcert": {
                new TeRun([
                    metadata: 'metadata/ipatests/ipa-getcert.yaml',
                    test: 'ipa-getcert'
                ]).exec('ipa-slave')
            },
            "bash::ipa-hbac-func": {
                new TeRun([
                    metadata: 'metadata/ipatests/ipa-hbac-func.yaml',
                    test: 'ipa-hbac-func'
                ]).exec('ipa-slave')
            },
            "bash::ssh-functional": {
                new TeRun([
                    metadata: 'metadata/ipatests/ipa-ssh-functional.yaml',
                    test: 'ipa-ssh-functional'
                ]).exec('ipa-slave')
            },
            "bash::user-cli-adduser": {
                new TeRun([
                    metadata: 'metadata/ipatests/adduser.yaml',
                    test: 'ipa-user-cli-adduser'
                ]).exec('ipa-slave')
            },
            "bash::client-cert": {
                new TeRun([
                    metadata: 'metadata/ipatests/ipa-client-cert.yaml',
                    test: 'ipa-client-cert'
                ]).exec('ipa-slave')
            },
            "bash::user-cli-moduser": {
                new TeRun([
                    metadata: 'metadata/ipatests/moduser.yaml',
                    test: 'ipa-user-cli-moduser'
                ]).exec('ipa-slave')
            },
            "bash::trust-functional-ssh": {
                new TeRun([
                    metadata: 'metadata/ipatests/ipa-trust-func-ssh.yaml',
                    test: 'ipa-trust-functional-ssh'
                ]).exec('ipa-slave')
            },
            "bash::trust-functional-user": {
                new TeRun([
                    metadata: 'metadata/ipatests/ipa-trust-func-user.yaml',
                    test: 'ipa-trust-functional-user'
                ]).exec('ipa-slave')
            }
            )
        }
}
