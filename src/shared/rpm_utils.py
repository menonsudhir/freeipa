"""
rpm - shared support utility functions
- check_rpm - Helper function to check if packages are installed
- list_rpms - Helper function to list installed rpms
- remove_rpm - Helper function to remove installed rpms
"""

import time
import pytest
from ipa_pytests.shared import paths


def list_rpms(host):
    """ list installed rpms """
    cmd = host.run_command([paths.RPM, '-qa', '--last'],
                           raiseonerr=False)
    if cmd.stdout_text:
        rpmlog_file = "/var/log/rpm.list." + time.strftime('%H%M%S',
                                                           time.localtime())
        host.put_file_contents(rpmlog_file, cmd.stdout_text)


def check_rpm(host, rpm_list):
    """
    Checks if packages belonging to specified in list 'rpm' exists.
    If not, then installs it.
    """
    print("\nChecking whether " + "".join(rpm_list) +
          " package installed on " + host.hostname)
    cmd_list = [paths.RPM, '-q']
    cmd_list.extend(rpm_list)
    print(cmd_list)
    output2 = host.run_command(cmd_list,
                               set_env=True,
                               raiseonerr=False)
    if output2.returncode != 0:
        print(" ".join(rpm_list) + " package not found on " +
              host.hostname + ", thus installing")
        yum_install = [paths.YUM, 'install', '-y']
        yum_install.extend(rpm_list)
        print(yum_install)
        install1 = host.run_command(yum_install,
                                    set_env=True,
                                    raiseonerr=False)
        if install1.returncode == 0:
            print(" ".join(rpm_list) + " package installed.")
        else:
            pytest.xfail(" ".join(rpm_list) + " package installation"
                         " failed, check repo links for further debugging")
    else:
        print("\n" + " ".join(rpm_list) + " package found on " +
              host.hostname + ", running tests")


def remove_rpm(host, rpm_list):
    """
    Removes the packages specified in rpm_list
    :param rpm_list:  list of packages to removed
    :return: None
    """
    print("Removing " + "".join(rpm_list) + "from " + host.hostname)
    cmd_list = [paths.RPM, '-e']
    cmd_list.extend(rpm_list)
    print(cmd_list)
    output = host.run_command(cmd_list,
                              set_env=True,
                              raiseonerr=False)
    if output.returncode != 0:
        print("Error in removing packages - " + "".join(cmd_list))
    else:
        print("Packages " + "".join(rpm_list) + "has been removed")


def get_rpm_version(host, rpm_list):
    "Get rpm version"
    run_cmd = [paths.RPM, '-q', rpm_list]
    output = host.run_command(run_cmd, raiseonerr=False)
    if output.returncode == 0:
        return output.stdout_text
    else:
        return ''

