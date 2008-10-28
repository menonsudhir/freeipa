# Authors:
#   Jason Gerard DeRose <jderose@redhat.com>
#
# Copyright (C) 2008  Red Hat
# see file 'COPYING' for use and warranty information
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; version 2 only
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA

"""
Various utility functions.
"""

import logging
import os
from os import path
import imp
import krbV
from constants import LOGGING_CONSOLE_FORMAT, LOGGING_FILE_FORMAT


def xmlrpc_marshal(*args, **kw):
    """
    Marshal (args, kw) into ((kw,) + args).
    """
    return ((kw,) + args)


def xmlrpc_unmarshal(*params):
    """
    Unmarshal (params) into (args, kw).
    """
    if len(params) > 0:
        kw = params[0]
        if type(kw) is not dict:
            raise TypeError('first xmlrpc argument must be dict')
    else:
        kw = {}
    return (params[1:], kw)


def get_current_principal():
    try:
        return krbV.default_context().default_ccache().principal().name
    except krbV.Krb5Error:
        #TODO: do a kinit
        print "Unable to get kerberos principal"
        return None


# FIXME: This function has no unit test
def find_modules_in_dir(src_dir):
    """
    Iterate through module names found in ``src_dir``.
    """
    if not (path.abspath(src_dir) == src_dir and path.isdir(src_dir)):
        return
    if path.islink(src_dir):
        return
    suffix = '.py'
    for name in sorted(os.listdir(src_dir)):
        if not name.endswith(suffix):
            continue
        py_file = path.join(src_dir, name)
        if path.islink(py_file) or not path.isfile(py_file):
            continue
        module = name[:-len(suffix)]
        if module == '__init__':
            continue
        yield module


# FIXME: This function has no unit test
def load_plugins_in_dir(src_dir):
    """
    Import each Python module found in ``src_dir``.
    """
    for module in find_modules_in_dir(src_dir):
        imp.load_module(module, *imp.find_module(module, [src_dir]))


# FIXME: This function has no unit test
def import_plugins_subpackage(name):
    """
    Import everythig in ``plugins`` sub-package of package named ``name``.
    """
    try:
        plugins = __import__(name + '.plugins').plugins
    except ImportError:
        return
    src_dir = path.dirname(path.abspath(plugins.__file__))
    for name in find_modules_in_dir(src_dir):
        full_name = '%s.%s' % (plugins.__name__, name)
        __import__(full_name)


def configure_logging(log_file, verbose):
    """
    Configure standard logging.
    """
    # Check that directory log_file is in exists:
    log_dir = path.dirname(log_file)
    if not path.isdir(log_dir):
        os.makedirs(log_dir)

    # Set logging level:
    level = logging.INFO
    if verbose:
        level -= 10

    log = logging.getLogger('ipa')

    # Configure console handler
    console = logging.StreamHandler()
    console.setLevel(level)
    console.setFormatter(logging.Formatter(LOGGING_CONSOLE_FORMAT))
    log.addHandler(console)

    # Configure file handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(level)
    file_handler.setFormatter(logging.Formatter(LOGGING_FILE_FORMAT))
    log.addHandler(file_handler)

    return log
