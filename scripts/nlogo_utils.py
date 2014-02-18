# -*- coding: utf-8 -*-
"""
Util methods related to netlogo
"""
import re

def modify_experiments_repetitions(filename, experiment, new_value, save = True):
    """
    It modifies the number of repetitions of all experiments
    in nlogo file.
    """
    # read nlogo file
    nlogo = open(filename, 'r')
    filedata = nlogo.read()
    nlogo.close()
    
    #  replace data
    toreplace = "repetitions=\"%s\"" % (new_value)
    filedata = re.sub('repetitions=\"\d+\"' , toreplace, filedata)
        
    # write new data    
    if save:
        nlogo = open(filename, 'w')
        nlogo.write(filedata)
        nlogo.close()    
    
#modify_experiments_repetitions("project.template/project.template.nlogo", 
#                                      "pilot5", 20, save = False)
