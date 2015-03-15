# Introduction #
We recently had some excellent video media about the space, including the Big 10 Network, Wayward Nation and a Starting Block video.  The idea behind this project is to have a TV monitor near the entrance so we can loop those videos for new folks coming in during open hours or members that have not seen them yet.

# Details #
We started with a Raspberry Pi image/video looper project from http://stevenhickson.blogspot.com/2014/05/rpi-video-looper-20.html.  That was a great starting point, then we added some extra capability to it, including the ability to also display images and more seamless transitions.  Some modifications:

additional pi setup:

```
# install a tool to display images directly to the frame buffer
sudo apt-get install fbi
# disable the desktop manager and thus X
sudo update-rc.d lightdm disable
```

of course change the pi user's password.

Additionally I edited /boot/config.txt to force the Pi into HDMI mode with audio and specify the group and mode to get proper resolution even if the pi boots with no TV attached.  These values might change depending on your HDMI device:
```
# uncomment if hdmi display is not detected and composite is being output
hdmi_force_hotplug=1
hdmi_drive=2
hdmi_group=1
hdmi_mode=4
```

and edit the /boot/cmdline.txt to add the following to make the console text black on black and no flashing cursor:

```
vt.global_cursor_default=0 loglevel=3 vt.default_red=0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0 vt.default_grn=0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0 vt.default_blu=0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
```

I also preferred FAT format for the USB card, so modifying /etc/fstab:

```
/dev/sda1       /media/USB      vfat    defaults,noatime,nodiratime     0      0
```

and finally some script modifications.  There is no need to start X:

### startfullscreen.sh ###
```
#!/bin/sh
`/home/pi/startvideos.sh`
```

and the most major changes are to startvideos.sh, to find and display/run images and python files (you can do cool things with a python direct to the framebuffer).  This script:

  * looks in /media and subfolders on the USB card (or locally depending on the configuration)
  * sorts by folder so you can group images
  * looks for a single image in /banner and if found just displays that
  * runs .py files found to enable a more dynamic slideshow, such as countdown timers.  If you don't have control over the physical device this is obviously a security concern.

### startvideos.sh ###
```
#!/bin/bash

declare -A vids

#Make a newline a delimiter instead of a space
SAVEIFS=$IFS
IFS=$(echo -en "\n\b")

usb=`cat /boot/looperconfig.txt | grep usb | cut -c 5- | tr -d '\r' | tr -d '\n'`

FILES=/home/pi/media/
SINGLE=/home/pi/banner/

if [[ $usb -eq 1 ]]; then
    FILES=/media/USB/media/
    SINGLE=/media/USB/banner/
fi

current=0
if [ -d "$SINGLE" ]; then
    echo "a single file only"
    file=`find $SINGLE -type f | tail -1 | egrep -i -e '\.(png|gif|jpg|jpeg)$'`
    echo "$file"
    /usr/bin/fbi -a -T 1 -d /dev/fb0 -noverbose "$file" 2>&1 > /dev/null
sleep 5
exit
fi

for f in `find $FILES -type f -print | sort | egrep -i -e '\.(mp4|avi|mkv|mp3|mov|mpg|flv|m4v|png|gif|jpg|jpeg|py)$'`
do
        vids[$current]="$f"
        let current+=1
        echo "$f"
done
max=$current
current=0

#Reset the IFS
IFS=$SAVEIFS

#case insensitive regex match
shopt -s nocasematch
while true; do
    if [ -f /boot/disabled.txt ]; then
      echo "disabled, exiting"
      exit
    fi
    #file=$FILES${vids[$current]}
    file=${vids[$current]}
    if [[ $file =~ \.(png|gif|jpg|jpeg)$ ]]; then
        #image file
        /usr/bin/fbi -a -T 1 -d /dev/fb0 -t 5 -1 -noverbose "$file" 2>&1 > /dev/null &
        #if these processes overlap the screen gets messed up
        sleep 5.5
        kill %1
    elif [[ $file =~ \.(mp4|avi|mkv|mp3|mov|mpg|flv|m4v)$ ]]; then
        #video file
        /usr/bin/omxplayer -o hdmi "$file" 2>&1 > /dev/null &
        wait
    elif [[ $file =~ \.(py)$ ]]; then
        #execute the python program
        python $file
    else
        echo "  unrecognized file format extension for: $file"
    fi
    let current+=1
    if [ $current -ge $max ]
    then
        current=0
    fi
done
```

# Sound #
To avoid the looping audio driving everyone batty we are using a Holosonic "Audio Spotlight" device to focus sound directly in front of the video screen.  Audio out is taken from the TV so we have a convenient audio level control.  This works, even perhaps a bit too well as the audio is focused very tightly for a group to watch.  Mounting the device to the ceiling and having it point directly down did make the audio cone a bit wider and more clear.

# Issues #
  * The device currently stops displaying output after many hours of playback.  I'm currently working to diagnose this issue.
  * It would be great if we could get our COBY TV to default to ON when plugged in.
  * The sound on the different video files is not at the same level, so it would be good to normalize those.