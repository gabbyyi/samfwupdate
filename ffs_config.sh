#!/bin/sh

modprobe libcomposite
mount -t configfs none /sys/kernel/config
cd /sys/kernel/config/
cd usb_gadget
mkdir g1
cd g1
echo "0x0456" > idVendor
echo "0x7031" > idProduct
echo "0x200" > bcdUSB
mkdir strings/0x409
echo "0" > strings/0x409/serialnumber
echo "1" > strings/0x409/manufacturer
echo "2" > strings/0x409/product

mkdir functions/ffs.usb0

mkdir configs/c.1
mkdir configs/c.1/strings/0x409
echo "USBi gadget" > configs/c.1/strings/0x409/configuration

ln -s functions/ffs.usb0 configs/c.1
cd /root
mkdir -p ffs
mount usb0 ffs -t functionfs
cd ffs
../ffs-test -d & sleep 3
cd ..

echo "musb-hdrc.3.auto" > /sys/kernel/config/usb_gadget/g1/UDC
