#!/bin/sh

cd /root

# this script starts the webpage demo.  it takes as an argument one of 
# the XML files for the corresponding demos

if [ $# -eq 0 ]; then
  echo "usage: rundemo.sh <schematic xml>" 
  exit
else
  if [ ! -f $1 ]; then
    echo $1 not found!
    exit
  fi
fi

 
# stop cores from running
corecontrol --stop 2
corecontrol --stop 1

# init codec (yes, do it twice)
./init1761 0 0x38
./init1761 0 0x38

# load sharcs with SS framework. (Important: Load core 2 1st)
./loadSharc -i SS_App_Core2.ldr -s 2 -d 1
./loadSharc -i SS_App_Core1.ldr -s 1 -d 1

# kill previous SS_App_linux process if running
kill -9 `ps | grep SS_App_linux | grep -v grep | sed -r 's/ root.*//g'`

# run SS framework ARM/linux portion  
./SS_App_linux &

# load in schematic using xml/cli parser.  Now user can control via webpage
# Blink on LED 11 to show demo is loading 
echo 50 > /sys/class/gpio/export 
echo out > /sys/class/gpio/gpio50/direction 

# load schematic and blink LED11
./SamXmlCli -D 1 -l $1  | xargs -I % sh -c 'expr 1 - `
cat /sys/class/gpio/gpio50/value` > /sys/class/gpio/gpio50/value'


# make sure LED11 is on when finished
echo 1 > /sys/class/gpio/gpio50/value

