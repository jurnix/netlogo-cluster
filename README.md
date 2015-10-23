Netlogo-cluster
=========

Netlogo-cluster is a tool to speed up the launch of big [Netlogo] [netlogo] experiments on a HPC with [SGE] [sge] scheduler. It uses netlogo headless and it takes advantage of the behaviourspace experiments (variable range, repetitions, number of cores, ...). Netlogo-cluster lets you launch:

 - A simple experimet with 1 job (multiple cores)
 - An experiment ranging step values with 1 or multiple variables with multiple jobs (multiple cores)
 - Multiple experiments combining both modes

This tool basically exploits the independance of each simulation to launch a lot of jobs at the same time. This is interesting for those experiments that require a lot of simulations. Be aware that it will not be useful when a single simulation is extremely complex so computational time becomes huge.


Introduction
--------------

Netlogo-cluster consists in the following files and folders:

* install.sh: install script to download and configure netlogo
* setenv.sh: environment configuration
* project.template: example of how to set up a project
* etc: configuration parameters
* docs: documentation folder
* scripts: python and bash script that implement functionalities

Installation
--------------

In order to install Netlogo-cluster you need to follow those commands:

```sh
./install.sh
```

To delete those downloaded files use **-clean**.

Create a new project
--------------

To create a new project you need to follow the steps found below.

1. Create a new folder

```sh
mkdir testproject
cd testproject
```

2. Copy your netlogo file with already defined experiments. If your netlogo model requires some data dependencies, be sure to copy them all in the right folder (probably in the projects root).
Netlogo model file must have the same as your projects folder. In this example: **testproject.nlogo**

3. Create **experiments** file and define the desired experiments.

4. Go to the netlogo-cluster root folder and execute the command:

```sh
cluster-launcher.py testproject
```

5. Wait

Define experiments
--------------

In order to run your experiments it is necessary to define them in **experiments** file. Define them in your behaviour space (remember its name). You will point them out into **experiments** file.

Each experiment defined in the file will be launch as a job. 

Find below the syntax:

*  Simple experiments
```
test1 50 01:00:00
test2 2000 25:00:00
```

Where each column represents:
1. experiments name: must be defined in the behaveour space and must have the same name
2. number of repetitions: overwrites the originaly value
3. maximum time: tells to HPC the maximum execution time for the whole simulation. After that, the SGE will kill the job.
There is no limit on the number of experiments

*   Complex experiments
```
test3 500 24:00:00 -parallelize VariableX 1 1 100
test4 200 24:00:00 -parallelize VariableX 0 0.1 1 -parallelize VariableY 0 0.1 1
```

The first 3 columns are the same as before except for the optional keyword *-parallelize* that defines:
1. -parallelize: declares to use multiple jobs for each step value
2. VariableX: name of the variable to apply the step value
3. 1: first value
4. 1: step size, every iteration is increased by this value
5. 100: last value (included)

In this case, it will launch 100 jobs into the HPC with 500 repetitions each.

Test4 is a little bit more complicated than test3 because there are 2 variables to parallelize. So when there is more than one value, netlogo-cluster **combines** with all possible options. In this case, there are 11 per each variable. Multiplying 11 x 11 results into 121 jobs to launch. Each one with 200 simulations.

**Note**: step range variables must be defined under behaviour space as **constant**. Netlogo-cluster will modify the nlogo file properly. 

Launch an experiment
----------------------

At the beginning of any work session you have to load linux environments. This way, you will be able to work with Netlogo-cluster from its parent folder.
It is expected to launch experiments from the root folder.

```sh
. setenv.sh
```

Type in your console in netlogo-cluster folder:

```sh
cluster-launcher.sh project.template
```

At this point you should see how netlogo-cluster is launching jobs.

Output
---------------------

Once all jobs are finished you may find a folder like this in your project. It contains the output data as well the input data (netlogo model, dependencies and experiments). The scripts will not never overwrite any folder so, at each new simulation, a new folder is created. 

* For simple experiments:
```
output_0_rep1000_11-02-2014
```

Where each column:
* output_: the same for all
* 0: job id number (increase by 1 unit each)
* rep1000: the number of simulation 
* 11-02-2014: date when the job was launched

* For complex experiments:
```
output_1.0_0_0_rep1000_11-02-2014
output_1.1_0.1_0_rep1000_11-02-2014
output_1.2_0.2_0_rep1000_11-02-2014
output_1.3_0.2_0_rep1000_11-02-2014
...
output_1.0_0_0.1_rep1000_11-02-2014
output_1.1_0.1_0.1_rep1000_11-02-2014
output_1.2_0.2_0.1_rep1000_11-02-2014
output_1.3_0.2_0.1_rep1000_11-02-2014
...
```

Everything is the same except for the job id number. At this point, it is shown a sub-id specifying what number has been used for that step value. After sub-id, it is shown the values taken in this simulation for each step range variable specified on experiments. They are in the same order as defined.

Results
---------

If everything was successful you should expect a file called **output** inside each folder with the netlogo model used for that specific simulation. 

[netlogo]:http://ccl.northwestern.edu/netlogo/
[sge]:http://en.wikipedia.org/wiki/Oracle_Grid_Engine

Licenses
---------

The code which makes up this Python project template is licensed under the MIT/X11 license. Feel free to use it in your free software/open-source or proprietary projects.	

Issues
---------

Please report any bugs or requests that you have using the Bitbucket issue tracker.

Author
---------

* Albert Jornet Puig

Contact
---------
For any question, bug, ... do not heasitate to contact with us:

* jurnix@gmail.com


[netlogo]:http://ccl.northwestern.edu/netlogo/
[sge]:http://en.wikipedia.org/wiki/Oracle_Grid_Engine
