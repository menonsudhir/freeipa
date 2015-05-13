"""
Certmonger query tests.
This is example code to build CA Certificate Renewal code
"""

import pytest
import time
import sys
import ast
from ipa_pytests.shared.qe_certs import QE_IPA_Certs

scripts_dir = "/usr/lib/python%s/site-packages/ipa_pytests/scripts" % sys.version[:3]
qe_getcerts = "/usr/bin/python %s/qe_ipa_getcerts.py" % scripts_dir
qe_certs = QE_IPA_Certs()


class TestUserA(object):
    """
    user_0001: ipa user-add basic test"
    """
    def class_setup(self, multihost):
        """ Setup for class """
        pass

    def test_list_certs_0001(self, multihost):
        """ list IPA certs """
        pytest.set_trace()
        cmd = multihost.master.run_command(qe_getcerts)
        qe_certs.set_certs(ast.literal_eval(cmd.stdout_text))
        latest = qe_certs.get_latest_expiration()
        current = int(multihost.master.run_command(['date', '+%s', '-u']).stdout_text)
        while current <= latest:
            soonest = qe_certs.get_soonest_expiration()
            for jump in qe_certs.ttls:
                if current < soonest - jump:
                    set_date = time.strftime('%m%d%H%M%Y', time.localtime(soonest - jump))
                    cmd = multihost.master.run_command(['date', set_date])
                    current = int(multihost.master.run_command(['date', '+%s', '-u']).stdout_text)
                time.sleep(300)
                cmd = multihost.master.run_command(qe_getcerts)
                qe_certs.set_certs(ast.literal_eval(cmd.stdout_text))
                resubmit = qe_certs.get_resubmit_status()
                next_soonest = qe_certs.get_soonest_expiration()
                if next_soonest > soonest:
                    break

            print "certs: ", qe_certs.certs
            print "current: ", time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(current))
            print "local: ", time.strftime('%m%d%H%M%Y', time.localtime(current))
            print "soonest: ", time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(soonest))
            print "latest: ", time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(latest))
            print "resubmit: ", resubmit

    def class_teardown(self, multihost):
        """ teardown for class """
        pass
