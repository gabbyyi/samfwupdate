#!/bin/sh

# test if PB1 is depressed 
echo 80 > /sys/class/gpio/export 
echo in > /sys/class/gpio/gpio80/direction
echo `cat /sys/class/gpio/gpio80/value`

# run POST if PB1 is pressed down, start USBi otherwise
if [ `cat /sys/class/gpio/gpio80/value` -eq 1 ]
then
	# run POST  
	echo "pb1 pressed... starting POST" 
	/root/post.sh
else
	# start USBi emulator
	echo "pb1 not pressed... starting USBi"
        /root/loadUSBi.sh

        # start web demo if usb cable is not plugged in
        sleep 5	

	#grep -q "buildroot user.info kernel: configfs-gadget gadget: high-speed config #1: c" /var/log
        grep -q "configfs-gadget" /var/log/messages
        if [ $? -eq 0 ]
        then
                echo "USB cable plugged in for USBi emulation.  Skipping web demo init"
        else
                echo "Initializing framework and schematic for web demo"
                /root/rundemo.sh /root/SAM-DualCore-Reverb-EQ.xml
        fi
fi


