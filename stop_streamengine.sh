# Stop script for python Tecsidel application & streamengine
echo "Stopping application"
EXECUTABLE_NAME_PYTHON="python *init.py"
PID=`ps -C "python *init.py" -o pid=`
kill -9 $PID
unset EXECUTABLE_NAME_PYTHON
unset PID
EXECUTABLE_NAME_ENGINE=streamengine.elf
PID=`ps -C streamengine.elf -o pid=`
kill -2 $PID
unset EXECUTABLE_NAME_ENGINE
unset PID
echo "Application Stopped"
#end of Stop script
