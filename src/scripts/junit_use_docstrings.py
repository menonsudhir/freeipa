import os
import argparse
import importlib
import xml.etree.ElementTree as ET

parser = argparse.ArgumentParser(description="Convert Junit XML test case names")
parser.add_argument('-i', '--input_file', help='Path to Junit XML Input file')
parser.add_argument('-o', '--output_file', help='Path to Junit XML Output file')
parser.add_argument('-t', '--team', help='Team Name to use in classname')
parser.add_argument('-s', '--suite', help='Suite Name to use in classname')
parser.add_argument('-p', '--package', help='Package Name to use in classname')
args = parser.parse_args()
input_file = args.input_file or '/tmp/junit.xml'
output_file = args.output_file or '/tmp/newjunit.xml'
team = args.team or 'RH'
team = team.upper()
suite = args.suite or None
pkg = args.package or None

# print args
# print "INPUT = " + input_file
# print "OUTPUT = " + output_file
# print "TEAM = " + team
# print "SUITE = " + str(suite)

tree = ET.parse(input_file)
for ts in tree.iter('testsuite'):
    for tc in ts.iter('testcase'):
        # print tc.tag, tc.attrib
        # print tc.attrib['classname']
        # print tc.attrib['name']

        class_list = tc.attrib['classname'].split('.')[::-1]
        class_name = class_list[0] if class_list[0:] else ""
        module_name = class_list[1] if class_list[1:] else ""
        suite_name = class_list[2] if class_list[2:] else ""
        src_name = class_list[3] if class_list[3:] else ""
        pkg_name = class_list[4] if class_list[4:] else ""

        if pkg_name is not "":
            pkg_name = pkg_name.replace('-', '_')

        if pkg is not None:
            pkg_name = pkg
        elif pkg_name is "":
            print("Unknown package.  Please specify on the command line")
            exit()

        if suite is not None:
            suite_name = suite
        elif suite_name is "":
            suite_name = os.path.basename(os.getcwd())

        if suite is not None:
            suite_nat = suite.replace('_', ' ').title()
        else:
            suite_nat = suite_name.replace('_', ' ').title()

        method_name = tc.attrib['name']
        # print suite_nat + "::" + module_name + "::" + class_name + "::" + method_name + "\n"

        try:
            my_mod = importlib.import_module(pkg_name + '.' + suite_name + '.' + module_name)
        except ValueError:
            print("Missing information for importing module to find docstring")
            exit()
        except ImportError as e:
            print(e)
            print("Invalid Module Path: %s" % pkg_name + '.' + suite_name + '.' + module_name)
            exit()

        my_class = getattr(my_mod, class_name)
        my_method = getattr(my_class, method_name)
        # print my_method.__doc__

        tc.attrib['name'] = team + "-TC: " + suite_nat + ": " + my_method.__doc__.strip()
        tc.attrib['classname'] = ""

tree.write(output_file)

print("New file written to " + output_file)
