#!/bin/sh

# We can use git on the board but might not work on pc testing if firewall 
# not configured properly.  Otherwise we can use http
GITPROT=git

# list of files to be updated
set boarddetect   \
    buttontest    \
    diytest       \
    ffs_config.sh \
    ffs-test      \
    init1761      \
    l2access      \
    ledtest       \
    loadSharc     \
    post.sh       \
    README.md     \
    rundemo.sh    \
    run.sh        \
    SAM-Audio-Testing_Core1.ldr    \
    SAM-DualCore-Reverb-EQ.dspproj \
    SAM-DualCore-Reverb-EQ.xml     \
    sampost.py    \
    SamXmlCli     \
    SS_App_Core1.dxe \
    SS_App_Core1.ldr \
    SS_App_Core2.dxe \
    SS_App_Core2.ldr \
    SS_App_linux  \
    updateSamFw.sh\
    UsbDeviceTest 

# This file is meant to be run from /root, which all the files reside.  The update script
# will git clone the lastest from github and then copy/install the files into /root

# save old update directory before git cloning new one 
if [ -d "$HOME/samfwupdate" ]; then
        echo "saving current update directory"
        if [ -d "$HOME/samfwupdate.backup.tgz" ]; then
		echo "samfwupdate.backup.tgz already exists.  Continue?"
#		if [ ] ; then
			rm $HOME/samfwupate.backup.tgz
#		fi
	fi

        # create back up tarball of current update dir 
	tar -czf $HOME/samfwupdate.backup.tgz  samfwupdate/

        # remove old update dire before git cloning
        echo "removing old update dir"
	rm -f $HOME/samfwupdate/* 
        rm -rf $HOME/samfwupdate/.git
	rmdir $HOME/samfwupdate
fi

# git clone the latest files from git
git clone $GITPROT://github.com/gabbyyi/samfwupdate.git

# install files cloned from git
for file in $@ 
do
	echo "installing $HOME/samfwupdate/$file" 
        cp $HOME/samfwupdate/$file .
done

