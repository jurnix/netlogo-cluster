# -*- coding: utf-8 -*-
"""
Modifies nlogo xml data 
"""
import mmap
import logging
import numpy as np

import xml.etree.ElementTree as ET    

# Logging system in INFO mode by default
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger("netlogo_xml")

START_TAG = """
@#$#@#$#@
@#$#@#$#@
@#$#@#$#@
"""

END_TAG = """
@#$#@#$#@
@#$#@#$#@
"""


def get_xml_data(filename):
    """
    Read file and search for xml data
    """
    content = None

    with open(filename, 'r') as f:
        content = f.read()

    xml_raw = content.split("@#$#@#$#@")[7]
    return ET.fromstring(xml_raw)    
    
    
def nlogo_step_values(filename, exp_name, variable, attr, new_value):
    """
    Generates all new lines that needs to be modified
    """
    output = None
    root = get_xml_data(filename)    

    # Select all experiments with a 
    # specific name and a retrieve the value of
    # its enumerates variables/data
    xpath = './experiment/[@name="%s"]/enumeratedValueSet[@variable="%s"]/value'

    try:
        # python 2.7
        total_finds = root.findall(xpath % (exp_name, variable))
    except: 
        #print "elementtree in version 2.6"
        allexps = root.findall('./experiment')
        for exp in allexps:
            if exp.attrib['name'] == exp_name:
                for att in exp.getiterator('enumeratedValueSet'):          
                    if att.attrib['variable'] == variable:
                        total_finds = att
			#print total_finds
    
    if not total_finds:
        raise Exception("Experiment \"%s\" not found" % exp_name)
    
    for elem in total_finds:
	#print "new value=", str(new_value)
        elem.set(attr, str(new_value))
        output = ET.tostring(root)
     
    return output
    

def replace(filename, new_xml):
    """
    Split files into chunks and then rebuilds it from scratch
    """
    fil = open(filename, 'r')
    
    # read whole file
    datafile = fil.read()
    fil.close()
    
    start_pos = datafile.find(START_TAG)
    end_pos = datafile.find(END_TAG, start_pos + len(START_TAG))        
    
    # split parts
    first_part = datafile[0:start_pos] + START_TAG
    last_part = datafile[end_pos:len(datafile)]
        
    # rebuild file
    return first_part + new_xml + last_part
    
    
def modify_nlogo_file(
    infile, experiment, nl_variable, attribute, new_value):        
    """
    It modifies a fixed value of a test for a defined variable. Then it saves
    the modified nlogo into a new file.
    """    
    new_xmls = nlogo_step_values(infile, experiment, \
                                   nl_variable, attribute, new_value)                                    
    #print new_xmls
    data = replace(infile, new_xmls)
    output = open(infile, 'w')
    output.write(data)
    output.close()
    

def count_steps_from_steppedValueSet(infile, experiment):
    """
    Given file and experiment it returns the number of combinations
    that steppedValueSet has.
    return -- int >= 0
    """
    log.info( "file to read %s" % infile)
    root = get_xml_data(infile) 
    xpath = './experiment/[@name="%s"]/steppedValueSet'
    total_steps = 0
    
    # python 2.7
    try:
        total_finds = root.findall(xpath % (experiment))    
    except:
        log.debug("pythyon version 2.6 for xpath")
        allexps = root.findall('./experiment')
        for exp in allexps:
            if exp.attrib['name'] == experiment:
                total_finds = exp.getiterator('steppedValueSet')
    
    for elem in total_finds:
        start = np.float(elem.attrib['first'])
        step = np.float(elem.attrib['step'])
        end = np.float(elem.attrib['last'])
        total_steps = ((end - start) / step) + 1
        log.info( "%s has %d values (%2.2f %2.2f %2.2f)" %\
                (elem.attrib['variable'], total_steps, start, step, end))
        
    return total_steps


def main():
    """Test method"""
    #inname = 'Ev.4.0.1/Ev.4.0.1.nlogo'
    inname = 'project.template/project.template.nlogo'
    print modify_nlogo_file(inname, 'test', 'PrbToBecomeAsymp', 'value', 0.1)
    print "steps to do", count_steps_from_steppedValueSet( \
                                inname, 'experiment_31_March_2013')
    
    
if __name__ == "__main__":
    main()
