import os
import sys 
import xml.etree.ElementTree as ET

test_suite =  os.environ['TEST_SUITE'].split("/")[-1].split(".")[0]
tree = ET.parse(sys.argv[1:][0])

root = tree.getroot()
for testcase in root.findall('testcase'):
  name = "IDM-IPA-TC : " + test_suite + " : "+ testcase.get('name')
  print name
  testcase.set('name', name)
tree.write(sys.argv[1:][0], encoding="utf-8", xml_declaration=True)
