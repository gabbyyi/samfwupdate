"""
"""


import sys,os
from time import sleep

_yellow = "\x1b[2;33m"
_green = "\x1b[2;32m"
_red = "\x1b[2;31m"
_white = "\x1b[2;37m"
_inverse = "\x1b[7m"
_blink = "\x1b[5m"
_normal = "\x1b[0m"
_analog_thres = 0x35
_digital_thres = 0x35
_default_timeout = 60 # seconds
_instruct = "\x1b[1m"


class Report:
    def __init__(self, header):
        mystring = _green+header+_white+"\n"
        self.string = mystring
        print mystring,

    def header(self, header):
        mystring = "\n"+_green+header+_white+"\n"
        self.string += mystring
        print
        print mystring,

    def testpass(self, result):
        mystring = (_green+result+_white+"\n")
        self.string += mystring
        print mystring,

    def testfail(self, result):
        mystring = (_red+result+_white+"\n")
        self.string += mystring
        print mystring,

    def data(self, result):
        mystring = (_yellow+result+_white+"\n")
        self.string += mystring
        print mystring,

    def myprint(self):
        print (_green+"\n\n---------------- Test Summary -----------------"+_white+"\n")
        print self.string


def testPB():
    return os.system('./buttontest'+' > /dev/null')


def leds(led):
    os.system('./ledtest '+str(led)+' > /dev/null')


def diy(led, datatype):
    return os.system('./diytest '+str(led)+' '+str(datatype)+' > /dev/null')


def ledtest(report):
    report.header("LED test")
    print _instruct+"Push and hold PB2 when done"+_normal
    atleastonce = False
    while 1:
        if atleastonce and (testPB() == 0x0200): break
        leds(0)
        sleep(0.5)
        if atleastonce and (testPB() == 0x0200): break
        leds(1)
        sleep(0.5)
        if atleastonce and (testPB() == 0x0200): break
        leds(2)
        sleep(0.5)
        if atleastonce and (testPB() == 0x0200): break
        leds(4)
        atleastonce = True
    report.testpass("LED test - Passed")
    report.testpass("PB2 test - Passed")
    return True


def buttonstuck(report):
    report.header("Button Stuck Test")
    print _instruct+"Please release buttons"+_normal
    retval = testPB()
    if retval == 0x0100: report.testfail("PB1 stuck")
    if retval == 0x0200: report.testfail("PB2 stuck")
    if retval == 0x0000:
        report.testpass("Button test pass")
        return True

    report.testfail("Button is stuck")
    return False


def buttontest(report):
    report.header("PB1 test")
    print _instruct+"Please push and hold PB1"+_normal
    timeout = _default_timeout*2
    while timeout > 0:
        retval = testPB()
        if retval == 0x100: break
        sleep(0.5)
        timeout -= 1
    if timeout == 0: 
        report.testfail("PB1 push NOT detected")
        report.testfail("PB1 test - Failed")
        return False

    report.testpass("PB1 push detected")
    report.testpass("Button test - Passes")
    return True


def ethernettest(report):
    print _instruct+"Please plug in the Ethernet cable"+_normal
    report.header("Waiting for Ethernet connection")
    try:
        fp = open("/sys/class/net/eth0/carrier")
    except Exception as e:
        report.testfail("Error opening carrier file: ")
        print format(e)

    wait = True
    timeout = _default_timeout*2 
    while wait:
        fp.seek(0)
        c = fp.read(1)
        if c == '1':
            wait = False
        sleep(0.5)
        timeout -= 1
        if timeout == 0:
            report.testfail("Cable NOT detected")
            report.testfail("Ethernet test - Failed")
            return False

    report.testpass("Ethernet test - Passed")
    return True


def waitforlinux(report):
    report.header("Waiting for Linux to finish booting")
    timeout = _default_timeout # seconds
    passed = False
    pool = False
    link = False
    while timeout and not passed:
        os.system('sync')
        with open("/var/log/messages") as fp:
            for line in fp:
                if 'random: nonblocking pool is initialized' in line:
                    pool = True
                if 'eth0: Link is Up' in line:
                    link = True
                if pool and link: 
                    passed = True
                    break

        timeout -= 1
        leds(7)
        sleep(0.5)
        leds(0)
        sleep(0.5)

    if passed:
        report.testpass("Linux Boot - Passed")
        report.testpass("Ethernet link - Passed")
        return True

    if not pool:
        report.testfail("Linux Boot - Failed")
    if not link:
        report.testfail("Ethernet link - Failed")

    return False


def usbtest(report):
    usbdevicepass = False
    usbhostpass = False
    report.header("Waiting for USB enumeration")
    timeout = _default_timeout
    while timeout > 0 and not (usbdevicepass and usbhostpass):
        timeout -= 1
        with open("/var/log/messages") as fp:
            for line in fp:
                if 'g_serial' in line:
                    if 'CDC ACM config' in line:
                        usbdevicepass = True
                if 'scsi host0' in line:
                    if 'usb-storage' in line:
                        usbhostpass = True
        sleep(1)

    if usbdevicepass:
        report.testpass("USB device connection detected")
    else:
        report.testfail("USB device not detected")

    if usbhostpass:
        report.testpass("USB host connection detected")
    else:
        report.testfail("USB host not detected")

    return usbdevicepass and usbhostpass


def initUSBdevice(report):
    report.header("Loading USB device driver")
    retval = os.system('modprobe g_serial')
    if retval == 0: 
        report.testpass("USB device driver loaded")
        return True
    report.testfail("USB device driver failed to load")
    return False


def audiotest(report):
    report.header("Audio Test")
    report.header("Loading SHARC's")
    # remove this first load after loadSharc is fixed
    retval = os.system('./loadSharc -i SAM-Audio-Testing_Core1.ldr -s 2')
    if retval:
        report.testfail("Failed to load SHARC's")
        return False
    retval = os.system('./loadSharc -i SAM-Audio-Testing_Core1.ldr -s 1')
    if retval:
        report.testfail("Failed to load SHARC's")
        return False

    sleep(1)

    # Verify SHARC code is running
    first = os.system('./l2access -r 0x20083000 -c 4 -q')
    second = first
    timeout = 30
    while timeout > 0 and second == first:
        sleep(1)
        second = os.system('./l2access -r 0x20083000 -c 4 -q')
        print second
        timeout -= 1

    if timeout == 0:
        report.testfail("Failed to detect SHARC execution")
        return False

    # Use l2access to read the audio status
    report.testpass("Detected SHARC execution")
    timeout = 30
    analogleftpass = False
    analogrightpass = False
    digitalleftpass = False
    digitalrightpass = False
    passed = False
    while timeout > 0 and not passed:
        analogleft   = os.system('./l2access -r 0x20083004 -c 4 -q')
        analogright  = os.system('./l2access -r 0x20083008 -c 4 -q')
        digitalleft  = os.system('./l2access -r 0x2008300C -c 4 -q')
        digitalright = os.system('./l2access -r 0x20083010 -c 4 -q')
        timeout -= 1

        if analogleft > _analog_thres:
            analogleftpass = True

        if analogright > _analog_thres:
            analogrightpass = True

        if digitalleft > _digital_thres:
            digitalleftpass = True

        if digitalright > _digital_thres:
            digitalrightpass = True

        if analogleftpass and analogrightpass and digitalleftpass and digitalrightpass:
            passed = True

    if passed:
        report.testpass("Audio system passed")
        return True

    report.testfail("Audio system failed")
    return False


def diytest(report):
    timeout = 20
    while( diy(0,0) == 0 ):
        print _instruct+"Push button on DIY board to start DIY test"+_normal
        timeout -= 1
        if timeout == 0: return True
        sleep(0.5)

    report.header("DIY board detected")
    print _instruct+"Push button and turn POT"+_normal
    print _instruct+"Verify operation by observing LED's"+_normal
    print _instruct+"Test ends when right button is pushed"+_normal

    runtest = True
    leds = 0
    testpassed = 0
    while( runtest ):
        button = diy(leds,0) >> 8
        if button == 16:
            leds = (diy(leds+1,2) >> 8) & 0x00F0
            testpassed |= 0x01
        if button == 4:
            leds = (diy(leds+2,3) >> 8) & 0x00F0
            testpassed |= 0x02
        if button == 2:
            leds = (diy(leds+4,1) >> 8) & 0x00F0
            testpassed |= 0x04
        if button == 1:
            diy(8,0)
            sleep(1)
            runtest = False

    if testpassed == 0x07:
        report.testpass("diytest complete")
        return True

    report.testfail("diytest complete")
    return False


def boarddetect(report):
    report.header("Board detection")
    board = os.system('./boarddetect'+' > /dev/null')
    report.data("Board ID = "+str(board))
    report.testpass("Board detect")
    return True


def main(argv):
    summary = Report("\nPost test version 1.2")
    print _instruct+"plug the board into a PC using the USB device connector"+_normal
    print _instruct+"Plug an Ethernet cable into the board and a PC configured for DHCP"+_normal
    print _instruct+"Connect the analog and digital audio loopbacks"+_normal
    print _instruct+"\n!! The USB flash stick should have been plugged in before power-up !!"+_normal
    print "\n"
    try:
        if not waitforlinux(summary): raise ValueError("waitforlinux")
        if not ledtest(summary): raise ValueError("ledtest")
        if not buttontest(summary): raise ValueError("buttontest")
        if not ethernettest(summary): raise ValueError("ethernettest")
        if not initUSBdevice(summary): raise ValueError("initUSBdevice")
        if not usbtest(summary): raise ValueError("usbtest")
        if not buttonstuck(summary): raise ValueError("buttonstuck")
        if not audiotest(summary): raise ValueError("audiotest")
        if not boarddetect(summary): raise ValueError("boarddetection")
        if not diytest(summary): raise ValueError("diytest")
    except ValueError:
        summary.myprint()
        print _red+"Post Failed"+_white+"\n"
        return -1

    summary.myprint()
    print _green+"Post Passed"+_white+"\n"
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
