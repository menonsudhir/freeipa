Installing
==========

This guide steps through installing ipa_pytests and prerequisites.  Steps
below indicate where to run commands as well as what.  The instructions here
typically describe installation on a centrally used "Test Runner" host.  The
purpose of running the test suites on a system not under test is to keep test
suite dependencies from being installed on the actual "Systems Under Test".
Regardless, these directions should also work for installation on an IPA
Master as well.  Or, really any node in the test environment.

Prerequisites
-------------

- On all hosts, setup yum repos for idmqe-extras-rhel.repo::

    wget -O /etc/yum.repos.d/idmqe-extras-rhel.repo \
        <url to repo>/idmqe-extras-rhel.repo

- Alternatively, you may prefer instead to use EPEL, especially if installing on
  a central server like a Jenkins Slave::

    yum install https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm

    yum install https://dl.fedoraproject.org/pub/epel/epel-release-latest-6.noarch.rpm

- On all hosts, add necessary Python tools/software/plugins::

    yum -y install \
        git \
        pylint \
        python-pip \
        python-ldap \
        PyYAML pytest \
        python-paramiko \
        python-coverage \
        python-requests \
        python-pytest-beakerlib \
        python-pytest-multihost \
        python-pytest-sourceorder

    pip install python-logstash

- Note: if using your own laptop/system as the Test Runner system, backup
  your existing user SSH keys first because the following would overwrite
  them.

- On Test Runner (or IPA Master that will execute tests), setup ssh keys::

    export MASTER=<Master_FQDN>
    export REPLICA=<Replica_FQDN>
    export CLIENT=<Client_FQDN>
    ssh-keygen -t rsa -N '' -C '' -f ~/.ssh/id_rsa
    cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys
    chmod 600 ~/.ssh/authorized_keys
    ssh-keyscan $MASTER >> ~/.ssh/known_hosts
    ssh-keyscan $REPLICA >> ~/.ssh/known_hosts
    ssh-keyscan $CLIENT >> ~/.ssh/known_hosts
    ssh-copy-id -i ~/.ssh/id_rsa $MASTER
    ssh-copy-id -i ~/.ssh/id_rsa $REPLICA
    ssh-copy-id -i ~/.ssh/id_rsa $CLIENT

Clone and Install
-----------------

- On Runner and all nodes under test install the project code::

    git clone <URL>
    cd ipa-pytests
    python setup.py install

Setup Code Coverage Support
---------------------------

This step is optional. If you want to gather test coverage statistics,
you can do so like this:

- Install coverage libraries::

    yum -y install python-coverage

- Setup coverage config to point to your specific site-packages path::

    cd /root/multihost_tests
    sed -i "s:SITEPACKAGES:/usr/lib/python<YOUR_VERSION_HERE>/site-packages:g" .coveragerc

- Add code coverage to run for all python by adding to site customize::

    cd /root/multihost_tests
    cat sitecustomize-add.py >> /usr/lib/python2.7/site-packages/sitecustomize.py

Setup pylint support
--------------------

This step is optional.  If you want to use pylint to scan the code,
you can add it and use the provided pylint config for the project.

- Install pylint::

    yum -y install pylint

- Use this pylint config file::

    pylint --rcfile=~/ipa-pytests/pylint.cfg <path to scan>
