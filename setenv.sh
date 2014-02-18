#!/bin/bash


PWD=`pwd`

export PATH=$PATH:$PWD/scripts
export NETLOGO_CLUSTER_PATH=$PWD

#ln -s  Netlogo-5.0.4 netlogo
export PYTHONPATH=$PYTHONPATH:`pwd`/scripts

source etc/netlogo-cluster.conf

echo "Configuration done"
