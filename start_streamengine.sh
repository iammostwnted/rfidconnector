#!/bin/bash
# Start script for streamengine
export PYTHONHOME=/
echo "Starting Streamengine..."
sleep 60
/apps/streamengine.elf &
# start python Tecsidel application
sleep 10
echo "Starting python application..."
python /apps/init.py --debug=info &
echo "Started applications in background"
#end of Start script
