#!/bin/bash
# vim: dict+=/usr/share/beakerlib/dictionary.vim cpt=.,w,b,u,t,i,k
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#   runtest.sh of /ipa-server/rhel74/pytest2bkr
#   Description: A generic job to run Pytest TC inside Beaker Job
#   Author: Abhijeet Kasurde <akasurde@redhat.com>
#
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#   Copyright (c) 2017 Red Hat, Inc.
#
#   This program is free software: you can redistribute it and/or
#   modify it under the terms of the GNU General Public License as
#   published by the Free Software Foundation, either version 2 of
#   the License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be
#   useful, but WITHOUT ANY WARRANTY; without even the implied
#   warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
#   PURPOSE.  See the GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program. If not, see http://www.gnu.org/licenses/.
#
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Include Beaker environment
. /usr/bin/rhts-environment.sh || exit 1
. /usr/share/beakerlib/beakerlib.sh || exit 1
. /etc/pytest_env.sh

PACKAGE="ipa-server ipa-server-dns selinux-policy pki-server"
pytest_location=/root/ipa-pytests
mh_cfg=$MH_CONF_FILE
junit_xml=${PYCONF_DIR}/${TESTCASE}.xml

rlJournalStart
    rlPhaseStartSetup
        echo "$MASTER" | grep -i "$(hostname)"
        if [ $? -eq 0 ]; then
            rlLog "Installing Packages [$PACKAGE]"
            yum install -y $PACKAGE

            for p in $PACKAGE
            do
                rlAssertRpm $p
            done
            rlLog "Install PyYAML"
            yum install -y PyYAML

            if [ -z $SRC_LOCATION ]; then
                SRC_LOCATION=http://git.app.eng.bos.redhat.com/git/ipa-pytests.git
            fi

            rlLog "Clone git repo ipa-pytests using $SRC_LOCATION"
            rlRun "git clone $SRC_LOCATION $pytest_location" 0

            rlLog "Install Pytest and dependencies"
            easy_install pip pytest pytest-multihost
            if [ $? -eq 0 ]; then
                if [ -d ${pytest_location} ]; then
                    pushd `pwd`
                    cd ${pytest_location}
                    python setup.py install
                    if [ $? -eq 0 ]; then
                        rlPass "Successfully install Pytest"
                    else
                        rlFail "Failed to install Pytest"
                    fi
                    popd
                fi
            else
                rlFail "Faild to install Pytest"
            fi
            rlPhaseEnd

            rlPhaseStartTest
            if [ -z ${TESTCASE} ]; then
                rlFail "Unable to find environment variable TESTCASE, please specify "\
                       "param with TESTCASE as name in task definiation"
            fi
            rlLog "Running testcase $TESTCASE"
            if [ -d ${pytest_location}/src/$TESTCASE -a -f $mh_cfg ];
            then
                pytest -s -v --multihost-config=${mh_cfg} --junit-xml=${junit_xml} ${pytest_location}/src/${TESTCASE}
                if [ $? -eq 0 ]; then
                    rlPass "$TESTCASE Passed"
                else
                    rlFail "$TESTCASE Failed"
                fi
            else
                rlFail "Failed to find Pytest src or multihost config file"
            fi
            rlRun "rhts-sync-set -s 'DONE' -m $MASTER"
        else
            rlLog "$(hostname) is not MASTER, so skipping operations and waiting for master"
            rlRun "rhts-sync-block -s 'DONE' $MASTER"
        fi
    rlPhaseEnd

rlJournalPrintText
rlJournalEnd
