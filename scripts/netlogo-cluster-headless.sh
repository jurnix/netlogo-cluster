#!/bin/sh
#$ -S /bin/bash 
#$ -V
#$ -cwd

cd $NETLOGO_CLUSTER_PATH   # the copious quoting is for handling paths with spacs
source "./etc/netlogo-cluster.conf"

if [ $# -eq 0 ]
  then
    echo ""
    echo "No arguments supplied\n"
    echo "Usage:"
    echo "   $0 modelFileName projects_name experimentsName"
    echo "   e.g $0 AntLines.nlogo oneexp" 
    echo ""
    echo "modelFileName: .nlogo file"
    echo "projects_name: name of the project"
    echo "experimentsName: you can create them through GUI, under Tools->BehaviorSpace. Then save the model and use the name you defined."
    exit 1
fi

#netlogo.jar is found
DIR=$NETLOGO_CLUSTER_PATH
NETLOGO_DIR=$DIR/$NETLOGO_FOLDER
PROJECT=$1
MODEL=$DIR/$PROJECT.nlogo
EXP=$2
#REP=$3
TH=$NETLOGO_THREADS
echo $dir
echo `ls -rtl`
echo "$0 model=$MODEL experiment=$EXP threads=$TH"
# search in model file for repetitions="NUMBER" and replaces for $repetitions var
# sed -e "s/repetitions=\"[[:digit:]]\+\"/repetitions=\"$REP\"/" -i $MODEL

# Java heap space of 1GB
# output: csv (better for big executions, it writes as it produces the output. But not with other options.)
echo "/usr/bin/time java -Xmx1024m -Dfile.encoding=UTF-8 -classpath `echo $NETLOGO_DIR`/NetLogo.jar org.nlogo.headless.Main --threads $TH --model $MODEL --experiment $EXP --table -"
/usr/bin/time java -Xmx1024m -Dfile.encoding=UTF-8 -classpath `echo $NETLOGO_DIR`/NetLogo.jar org.nlogo.headless.Main --threads $TH --model $MODEL --experiment $EXP --table -
