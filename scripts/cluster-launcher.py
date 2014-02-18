#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This scripts is a tool to launch jobs to an HPC with a SGE scheduler for Netlogo software.
"""
import os, sys
import shutil
import logging
import datetime
import argparse
import subprocess
import numpy as np

from itertools import product

#from scripts.settings import NETLOGO_THREADS
from scripts.netlogo_xml import modify_nlogo_file, \
                                count_steps_from_steppedValueSet
from scripts.nlogo_utils import modify_experiments_repetitions

NAME = "cluster-launcher.py"
RELEASE_DATE = "RELEASE_DATE_REPLACE"
VERSION = "VERSION_REPLACE"

PROGRAM = 'scripts/netlogo-cluster-headless.sh'

EXPERIMENTS ='experiments'

PARALLEL_TAG ='-parallelize'


EXP_NAME_ARRAY = 0
REP_ARRAY = 1
EXP_TIME_ARRAY = 2

# Experiments parallel parsed data
EXP_ARRAY_FIELD = 0
EXP_ARRAY_VARIABLE = 1
EXP_ARRAY_START = 2
EXP_ARRAY_END = 4
EXP_ARRAY_STEP = 3

# dictionary keys of generated values to launch to cluster
PARALLEL_DICT_NAME = 'name'
PARALLEL_DICT_DATA = 'data'

NETLOGO_ATTR = 'value'

# Arguments definition
parser = argparse.ArgumentParser(description='Automatize the launch of netlogo experiments to a cluster.')
parser.add_argument('project', nargs=1, help='Project\'s folder')
parser.add_argument('--debug', action='store_const', const=True,
                    default=False, help='Run script in debug mode.')
parser.add_argument('--version', action='version',
                    version='%(prog)s version=%(v)s, release date=%(rd)s' \
                    % {'prog': NAME,'v': VERSION, 'rd': RELEASE_DATE})

# Logging system in INFO mode by default
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger("cluster-launcher")

try:
    NETLOGO_THREADS=int(os.environ['NETLOGO_THREADS'])
except KeyError:
    print "Remember to load the environment with ./setenv.sh"
    sys.exit(1)


def run_linux_cmd(cmd):
    log.debug( "linux cmd => %s" % cmd)
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    (output, err) = p.communicate()
    log.debug(output.strip())

    if err:
        log.error(err.strip())

def create_output_folder(project, folderName):
    """
    Create a new output folder. Then it copy experiment and nlogo file used
    for that experiment.
    """
    if os.path.exists(folderName):
        raise Exception("Folder '%s' already exists" % folderName)
        
    srcexp = project + '/' + EXPERIMENTS
    src_nlogo = project + '/' + project + '.nlogo'
        
    os.makedirs(folderName)
    shutil.copy(srcexp, folderName)
    shutil.copy(src_nlogo, folderName)

    # creat symlink of extra data to each folder
    for file_name in next(os.walk(project))[2]:
        if not file_name.startswith(('exp', project)) and not file_name.endswith('nlogo'):            
            os.symlink('../' + file_name, folderName + '/' + file_name)

def generate_values_to_parallelize(raw_data):
    """
    Transform raw parsed data to a dict with all values for each variable
    """
    values_to_test = []
    for parallel_data in raw_data:
        start = float(parallel_data[EXP_ARRAY_START])
        end = float(parallel_data[EXP_ARRAY_END])
        step = float(parallel_data[EXP_ARRAY_STEP])
        data = dict()
        data[PARALLEL_DICT_DATA] = np.arange(start, end+step, step)
        data[PARALLEL_DICT_NAME] = parallel_data[EXP_ARRAY_VARIABLE]
        values_to_test.append(data)
        
    return values_to_test

def launch_job(
    project, experiment, repetitions, expected_time, paralls ):
    """
    Send job to cluster. It also make generate all comibinations possible
    when is required for the optional parallelization option.
    """    

    modelname = project + "/" + project + ".nlogo"
    
    next_folder_id = get_latest_output_id(project) + 1
    today = datetime.datetime.now().strftime("%d-%m-%Y")
    
    multiplier = count_steps_from_steppedValueSet(modelname, experiment)
    log.debug("repetitions set to %f(before %f) because of steppedValueSet" % \
            (float(multiplier) * float(repetitions), float(repetitions)))
    total_repetitions = int(repetitions) #int(multiplier) * 
    
    #log.debug("Repetitions set to %d because of steppedValues" % \
    #            (total_repetitions))
    # set repetitions to nlogo file
    modify_experiments_repetitions(modelname, experiment, total_repetitions)
    
    if paralls:
        log.debug('parallel execution')
        values_to_par = generate_values_to_parallelize(paralls)
        
        # extract the length of each dataset
        values_length = [len(x[PARALLEL_DICT_DATA]) for x in values_to_par]
        jobs_to_launch = np.array(values_length).prod()
        log.debug("jobs to launch = %s " % jobs_to_launch)
        
        # get all permutations
        dataset = [x[PARALLEL_DICT_DATA] for x in values_to_par]
        for i in range(0, len(values_to_par)):
            log.debug("Each job %s takes this values %s" % \
                    (values_to_par[i][PARALLEL_DICT_NAME], dataset[i]))
        
        # launch all jobs
        for counter, data_tuple in enumerate(product(*dataset)):
            vars_values = ''
            log_data_tmp = "Data set to "
                       
            # replaces for each defined value for the new value 
            for i, elem in enumerate(data_tuple):
                varname = values_to_par[i][PARALLEL_DICT_NAME]
                vars_values = vars_values + str(elem) + "_"
                log_data_tmp = log_data_tmp + str(varname) + "=" + str(elem) + ", "#("modify_nlogo_file(%s, %s, %s, %s, %s" % (modelname, experiment, varname, NETLOGO_ATTR, elem))
                modify_nlogo_file(modelname, experiment, varname, NETLOGO_ATTR, elem)
            
            output_path = project + "/output_%d.%d_%s%s_rep%s_%s" % \
                (next_folder_id, counter, vars_values, experiment, total_repetitions, today)

            params = "%s %s %s" % (output_path + '/' + project, experiment, total_repetitions)
         
            # creates a new folder    
            create_output_folder(project, output_path)
            cmd = "qsub -pe smp %d -o %s/output -e %s/output.err -l h_rt=%s %s %s" % \
            (NETLOGO_THREADS, output_path, output_path, expected_time, PROGRAM, params)
            
            log.debug("%s --> job sent" % log_data_tmp)
            run_linux_cmd(cmd)
    else:
        output_path = project + "/output_%d_rep%s_%s" % \
                    (next_folder_id, repetitions, today)
   
        params = "%s %s %s" % (output_path + '/' + project, experiment, total_repetitions)
 
        create_output_folder(project, output_path)
        cmd = "qsub -pe smp %d -o %s/output -e %s/output.err -l h_rt=%s %s %s" % \
        (NETLOGO_THREADS, output_path, output_path, expected_time, PROGRAM, params)
        
        run_linux_cmd(cmd)
    
    
def extract_parallelizations(data):
    """ Parse parallelizations experiments arguments into lists """
    parall_counter = 0    
    output = []
    
    for i, elem in enumerate(data.split()):
        if elem == PARALLEL_TAG or parall_counter > 0:
            if parall_counter == 0:
                #print "==> init list"
                new_element = list()                        
            
            #print "element added ==>", elem
            new_element.append(elem)
            parall_counter = parall_counter + 1
            
        if parall_counter == 5:
            #print "==> end list"
            output.append(new_element)
            parall_counter = 0
        
    return output
            

def parse_experiment(data):
    """ Parse an experiments line  """
    array_data = data.split()
    exp_name = array_data[EXP_NAME_ARRAY]
    repetitions = array_data[REP_ARRAY]
    expected_time = array_data[EXP_TIME_ARRAY]
    parallelizations = extract_parallelizations(data[2:])
    return exp_name, repetitions, expected_time, parallelizations
    
def get_latest_output_id(folder):
    """ Search for the highest id output given a project """
    path = "./%s/" % (folder)

    # list subfolders
    sub_folders = [name for name in os.listdir(path) if os.path.isdir(os.path.join(path, name))]
    
    if not sub_folders:
        return -1
        
    # filter folder and search for id output number
    # split by _ and then by .
    ids = [int(x.split('_')[1].split('.')[0]) for x in sub_folders if x.startswith('output')]
    
    if not ids:
        return -1
    
    return max(ids)
                    
def main():
    
    results = parser.parse_args()  
    project = results.project[0]
    log.info("Launching project %s" % project)
    
    experiments = open(project + "/" + EXPERIMENTS, 'r')
        
    # treat each experiment
    for experiment in experiments:
        exp_name, repetitions, expected_time, paralls = parse_experiment(experiment)
        
        launch_job(project, exp_name, repetitions, expected_time, paralls)        

if __name__ == "__main__":
    main()
