#!/usr/bin/env python
from lxml import etree

def setup_xml(xml_file):
    # Load xml file
    file = etree.parse(xml_file)
    # Finds the root tag
    root = file.getroot()

    # Change VM name tag: takes the xml_file name without the extension
    name_tag = root.find("name")
    name_tag.text = xml_file.split('.')[0]

    # Change brige type of source tag to 'virbr0'
    source_tag = root.find("./devices/interface/source")
    source_tag.set("bridge", "virbr0")
    
    # Save the changes
    file_saved = open(xml_file, 'w')
    file_saved.write(etree.tostring(root, pretty_print=True))
    file_saved.close()

setup_xml("tests.xml")
# from lxml import etree
# tree = etree.parse('books.xml')

# new_entry = etree.fromstring('''<book category="web" cover="paperback">
# <title lang="en">Learning XML 2</title>
# <author>Erik Ray</author>
# <year>2006</year>
# <price>49.95</price>
# </book>''')

# root = tree.getroot()

# root.append(new_entry)

# f = open('books-mod.xml', 'w')
# f.write(etree.tostring(root, pretty_print=True))
# f.close()