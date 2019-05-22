@Library('idm-ci')
import idmci.*

properties([
    gitLabConnection('idm-jenkins'),
    pipelineTriggers([
        gitlab(
            triggerOnPush: true,
            triggerOnMergeRequest: true, triggerOpenMergeRequestOnPush: "never",
            triggerOnNoteRequest: true,
            noteRegex: "Jenkins please retry a build",
            skipWorkInProgressMergeRequest: true,
            ciSkip: true,
            setBuildDescription: true,
            addNoteOnMergeRequest: true,
            addCiMessage: true,
            addVoteOnMergeRequest: true,
            acceptMergeRequestOnSuccess: false,
            branchFilterType: 'All')
    ])
])

env.IDMPIPELINE_GITREPO = 'https://gitlab.cee.redhat.com/identity-management/ipa-pytests.git'
env.IDMCI_GITREPO = 'https://gitlab.cee.redhat.com/identity-management/idm-ci.git'
env.IPA_EMAIL = 'ipa-and-samba-team-automation@redhat.com'
env.ANSIBLE_GATHER_TIMEOUT = '60'

node {
    gitlabBuilds(builds: ['tier-1']) {
        stage("tier-1") {
          parallel(
            "pytest::ipa-hosts": {
                new TeRun([
                    metadata: 'metadata/pytests/ipa-host.yaml',
                    test: 'pytests-ipa-host'
                ]).exec('upshift-slave')
            },
            "pytest::func-svcs": {
                new TeRun([
                    metadata: 'metadata/pytests/functional_services.yaml',
                    test: 'ipa-functional-services',
                ]).exec('upshift-slave')
            },
            "pytest::idoverride": {
                new TeRun([
                    metadata: 'metadata/pytests/ipa-idoverride.yaml',
                    test: 'ipa-idoverride',
                ]).exec('upshift-slave')
            },
            "pytest::subca": {
                new TeRun([
                    metadata: 'metadata/pytests/subca.yaml',
                    test: 'ipa-subca',
                ]).exec('upshift-slave')
            },
            "pytest::rbac": {
                new TeRun([
                    metadata: 'metadata/pytests/ipa-rbac.yaml',
                    test: 'ipa-rbac',
                ]).exec('upshift-slave')
            },
            "pytest::external-ca": {
                new TeRun([
                    metadata: 'metadata/pytests/external-ca.yaml',
                    test: 'ipa-external-ca',
                ]).exec('upshift-slave')
            },
            "pytest::ca_cert_renewal": {
                new TeRun([
                    metadata: 'metadata/pytests/ca_cert_renewal.yaml',
                    test: 'ca_cert_renewal',
                ]).exec('upshift-slave')
            },
            "pytest::otp": {
                new TeRun([
                    metadata: 'metadata/pytests/otp.yaml',
                    test: 'otp',
                ]).exec('upshift-slave')
            },
            "pytest::vault": {
                new TeRun([
                    metadata: 'metadata/pytests/vault.yaml',
                    test: 'vault',
                ]).exec('upshift-slave')
            },
            "pytest::replica-install": {
                new TeRun([
                    metadata: 'metadata/pytests/replica-install.yaml',
                    test: 'ipa-replica-install',
                ]).exec('upshift-slave')
            },
            "pytest::replica-promotion": {
                new TeRun([
                    metadata: 'metadata/pytests/ipa-replica-promotion.yaml',
                    test: 'ipa-replica-promotion',
                ]).exec('upshift-slave')
            },
            "bash::krbtpolicy": {
                new TeRun([
                    metadata: 'metadata/ipatests/ipa-krbtpolicy.yaml',
                    test: 'ipa-krbtpolicy'
                ]).exec('upshift-slave')
            },
            "bash::dns": {
                new TeRun([
                    metadata: 'metadata/ipatests/ipa-dns.yaml',
                    test: 'ipa-dns'
                ]).exec('upshift-slave')
            },
            "bash::sudo": {
                new TeRun([
                    metadata: 'metadata/ipatests/ipa-sudo.yaml',
                    test: 'ipa-sudo'
                ]).exec('upshift-slave')
            },
            "bash::password": {
                new TeRun([
                    metadata: 'metadata/ipatests/ipa-password.yaml',
                    test: 'ipa-password'
                ]).exec('upshift-slave')
            },
            "bash::cert": {
                new TeRun([
                    metadata: 'metadata/ipatests/ipa-cert.yaml',
                    test: 'ipa-cert'
                ]).exec('upshift-slave')
            },
            "bash::getcert": {
                new TeRun([
                    metadata: 'metadata/ipatests/ipa-getcert.yaml',
                    test: 'ipa-getcert'
                ]).exec('upshift-slave')
            },
            "bash::ipa-hbac-func": {
                new TeRun([
                    metadata: 'metadata/ipatests/ipa-hbac-func.yaml',
                    test: 'ipa-hbac-func'
                ]).exec('upshift-slave')
            },
            "bash::ssh-functional": {
                new TeRun([
                    metadata: 'metadata/ipatests/ipa-ssh-functional.yaml',
                    test: 'ipa-ssh-functional'
                ]).exec('upshift-slave')
            },
            "bash::user-cli-adduser": {
                new TeRun([
                    metadata: 'metadata/ipatests/adduser.yaml',
                    test: 'ipa-user-cli-adduser'
                ]).exec('upshift-slave')
            },
            "bash::client-cert": {
                new TeRun([
                    metadata: 'metadata/ipatests/ipa-client-cert.yaml',
                    test: 'ipa-client-cert'
                ]).exec('upshift-slave')
            },
            "bash::user-cli-moduser": {
                new TeRun([
                    metadata: 'metadata/ipatests/moduser.yaml',
                    test: 'ipa-user-cli-moduser'
                ]).exec('upshift-slave')
            },
            "bash::trust-functional-ssh": {
                new TeRun([
                    metadata: 'metadata/ipatests/ipa-trust-func-ssh.yaml',
                    test: 'ipa-trust-functional-ssh'
                ]).exec('upshift-slave')
            },
            "bash::trust-functional-user": {
                new TeRun([
                    metadata: 'metadata/ipatests/ipa-trust-func-user.yaml',
                    test: 'ipa-trust-functional-user'
                ]).exec('upshift-slave')
            }
            )
        }
    }
}
