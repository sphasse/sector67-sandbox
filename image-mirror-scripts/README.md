# Introduction
This directory holds scripts to automate image archives from Sector67.  To start the process, run:

```
./archive-images.sh
```

You will need an ssh key with appropriate remote permissions.

The script also sends email status and the host needs to be properly configured to send emails.  The ../setup directory contains some information on that.

ssmtp has been deprecated, so you will need to set up something like msmtp on the raspberry pi, and make sure it is working properly:

```
sudo apt-get install msmtp msmtp-mta
```

with an appropriate `/etc/msmtprc` file for your gmail account or however you are sending email.

An ssh key needs to be established, and if stored on a FAT format USB drive will not be able to be assigned the appropriate permissions to work properly.  Therefore it is common to create an SSH key in the user's home directory .ssh subdirectory and reference it there.

A cron job can be established to automatically run the job, e.g.

```
0 2 * * * cd /media/pi/SECTOR67-A/camera-archive; ./archive-and-email.sh
``` 


