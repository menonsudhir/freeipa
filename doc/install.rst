Installing
==========

This guide steps through installing ipa_pytests and prerequisites.  Steps
below indicate where to run commands as well as what.  This is for running on
hosts that will be a part of the IPA tests.  So, some hosts may be referred to
as Master, Replica, or Clients.  This refers to server role in IPA.

Prerequisites
-------------

- On all hosts, setup yum repos for idmqe-extras-rhel.repo::

    wget -O /etc/yum.repos.d/idmqe-extras-rhel.repo \
        <url to repo>/idmqe-extras-rhel.repo

- On all hosts, add necessary Python tools/software/plugins::

    yum -y install \
        PyYAML pytest \
        python-paramiko \
        python-pytest-beakerlib \
        python-pytest-multihost \
        python-pytest-sourceorder

- On Master (or main host that will execute tests), setup ssh keys::

    export MASTER=<Master_FQDN>
    export REPLICA=<Replica_FQDN>
    export CLIENT=<Client_FQDN>
    ssh-keygen -t rsa -N '' -C '' -f ~/.ssh/id_rsa
    cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys
    chmod 600 ~/.ssh/authorized_keys
    ssh-keyscan $MASTER >> ~/.ssh/known_hosts
    ssh-keyscan $REPLICA >> ~/.ssh/known_hosts
    ssh-keyscan $CLIENT >> ~/.ssh/known_hosts
    ssh-copy-id -i ~/.ssh/id_rsa $REPLICA
    ssh-copy-id -i ~/.ssh/id_rsa $CLIENT

Clone and Install
-----------------

- On Master, download project code::

    git clone <URL>

- On Master, install locally (Optional)::

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
