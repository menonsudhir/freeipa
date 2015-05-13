Installing
==========

This guide steps through installing idm_qe_ipa_tests and prerequisites.  Steps
below indicate where to run commands as well as what.  This is for running on 
hosts that will be a part of the IPA tests.  So, some hosts may be referred to
as Master, Replica, or Clients.  This refers to function in IPA.

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


Clone and Install
-----------------

- On Master, download project code::

    git clone <URL>

- On Master, install locally (Optional)::

    cd idm_qe_ipa_tests
    python setup.py install


