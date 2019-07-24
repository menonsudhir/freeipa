"""
Certmonger query tests.
This is example code to build CA Certificate Renewal code
"""

import time
import sys
import ast
import pytest
from ipa_pytests.shared.qe_certs import QE_IPA_Certs

qe_certs = QE_IPA_Certs()


def renew_certs(host):
    """ list IPA certs """
    script1 = "/usr/local/lib/python%s/site-packages/ipa_pytests/scripts/qe_ipa_getcerts.py" % sys.version[:3]
    script = "/root/qe_ipa_getcerts.py"
    f = open(script1).read()
    host.transport.put_file_contents(script, f)
    cmd = host.run_command(['/usr/libexec/platform-python', script])
    qe_certs.set_certs(ast.literal_eval(cmd.stdout_text))
    latest = qe_certs.get_latest_expiration()
    current = int(host.run_command(['date', '+%s', '-u']).stdout_text)
    while current <= latest:
        soonest = qe_certs.get_soonest_expiration()
        for jump in qe_certs.ttls:
            if current < soonest - jump:
                set_date = time.strftime('%m%d%H%M%Y', time.localtime(soonest - jump))
                cmd = host.run_command(['date', set_date])
                current = int(host.run_command(['date', '+%s', '-u']).stdout_text)
            time.sleep(300)
            cmd = host.run_command(['/usr/libexec/platform-python', script])
            qe_certs.set_certs(ast.literal_eval(cmd.stdout_text))
            resubmit = qe_certs.get_resubmit_status()
            if resubmit != 0:
                return(resubmit, current)
            next_soonest = qe_certs.get_soonest_expiration()
            if next_soonest > soonest:
                break

        print("certs: ", qe_certs.certs)
        print("current: ", time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(current)))
        print("local: ", time.strftime('%m%d%H%M%Y', time.localtime(current)))
        print("soonest: ", time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(soonest)))
        print("latest: ", time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(latest)))
        print("resubmit: ", resubmit)
