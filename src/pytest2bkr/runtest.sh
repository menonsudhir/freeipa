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

PACKAGES="ipa-server ipa-server-dns selinux-policy pki-server firefox xorg-x11-server-Xvfb PyYAML"
pytest_location=/root/ipa-pytests
mh_cfg=$MH_CONF_FILE
junit_xml=${PYCONF_DIR}/${TESTCASE}.xml
gecko_driver=https://github.com/mozilla/geckodriver/releases/download/v0.12.0/geckodriver-v0.12.0-linux64.tar.gz
pytest_ver=3.2.1
selenium_ver=3.4.3

install_pytest() {
    rlPhaseStartTest "Installing Pytest and required dependencies"
        rlLog "Installing Packages [$PACKAGES]"
        yum install -y $PACKAGES
        for p in $PACKAGES
        do
            rlAssertRpm $p
        done

        if [ -z $SRC_LOCATION ]; then
            SRC_LOCATION=http://git.app.eng.bos.redhat.com/git/ipa-pytests.git
        fi

        rlLog "Clone git repo ipa-pytests using $SRC_LOCATION"
        rlRun "wget $gecko_driver" 0
        rlRun "tar xvzf geckodriver-v0.12.0-linux64.tar.gz" 0
        rlRun "mv geckodriver /usr/bin/" 0

        if [ -z $BRANCH ]; then
            BRANCH="master"
        fi

        SSL="GIT_SSL_NO_VERIFY=false"
        if [ ! -z $SSL_NO_VERIFY ]; then
            SSL="GIT_SSL_NO_VERIFY=true"
        fi

        rlLog "Clone git repo ipa-pytests using $SRC_LOCATION using branch $BRANCH"
        rlRun "${SSL} git clone -b $BRANCH $SRC_LOCATION $pytest_location" 0


        rlLog "Install Pytest and dependencies"
        rlLog "Going to install : pytest==$pytest_ver pytest-multihost pyvirtualdisplay selenium==$selenium_ver"
        easy_install pip
        pip install pytest==$pytest_ver pytest-multihost pyvirtualdisplay selenium==$selenium_ver PyYAML --index https://pypi.org/simple/
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
}

rlJournalStart
    rlPhaseStartSetup
        echo "$MASTER" | grep -i "$(hostname)"
        if [ $? -eq 0 ]; then
            install_pytest
            if [ -z ${TESTCASE} ]; then
                rlFail "Unable to find environment variable TESTCASE, please specify "\
                       "param with TESTCASE as name in task definition"
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
            install_pytest
            rlLog "$(hostname) is not MASTER, so skipping operations and waiting for master"
            rlRun "rhts-sync-block -s 'DONE' $MASTER"
        fi
    rlPhaseEnd

rlJournalPrintText
rlJournalEnd
