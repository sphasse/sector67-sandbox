# Introduction #

This exercise is a part of the Sector67 [EMC2IntegrationClass](EMC2IntegrationClass.md).  In this exercise you will create a virtual EMC2 instance using VirtualBox and the EMC2 live CD.

VirtualBox is open source virtualization software, much like !VMWare Workstation or Parallels.

This virtual EMC2 instance will be used during the class to obtain familiarity with the EMC2 installation process, EMC2 configuration, the various user interfaces and to practice creation of integrations such as custom user space components and classic ladder programs.

# Details #
## Pre-requisite software ##
You will need the following software:

A VirtualBox install appropriate for your PC, available from [the VirtualBox site](https://www.virtualbox.org/wiki/Downloads).  This example uses VirtualBox 4.1.6.

The EMC2 Ubuntu 10.04 live CD iso image, available from [the EMC2 site](http://www.linuxcnc.org/)

## Virtual machine creation ##
After following the installation instructions for your platform, start VirtualBox and run "Machine->New...".  This should start the new virtual machine wizard.  Click "Next" to continue.  You will then need to choose a name for your virtual machine, such as "EMC2Sandbox".  For the "Operating System" and "Version" choose "Linux" and "Ubuntu".  Click "Next".

For the base memory size, you can choose 512MB.  For the Start-up disk, choose to create a new hard disk, choose the VDI type disk and click "Next".  A dynamically allocated disk will be fine for our EMC2 sandbox.  The default Location and 4 GB should be sufficient for the hard disk size.  Click "Next" to continue to installation wizard, and click "Create" to create the virtual machine.

## Installing EMC2 ##
After the virtual machine is created, we'll need to configure it to boot from the EMC2 live CD iso image.  An actual burned CD is not necessary, but could alternatively be used for the installation (but would be significantly slower).

With your virtual machine instance highlighted, click "Settings".  Under the "storage" tab, select the "Empty" CD icon under the "IDE Controller" and click the CD icon on the far right to set up the CD/DVD drive.  If installing from an iso image, select "Choose a virtual CD/DVD disk file..." and browse to the location of your live CD and choose the .iso file.  Click OK and

Then click "Start" to start the virtual machine.  You may see a couple of warnings and should then see the Ubuntu boot process.

We'll use the live CD to install a local copy, which is the same process that would be used for a real mill.

Once Ubuntu has booted completely, click the "Install Ubuntu 10.04 LTS" icon.  "LTS" stands for long-term support and it is used to designate versions of Ubuntu that are commercially-supported for a long term.

NOTE: _Alternatively at this point you could run EMC2 or any of the utilities directly from the live CD.  This is useful to test the latency of a PCs without doing a full install._

Clicking the install icon will start the installation wizard.  Choose your language, location, keyboard layout.  Choose to erase and use the entire disk you allocated during machine creation.  Choose an account and password and give the PC an appropriate name.  It will be most convenient if you choose to "Log in Automatically", however you will still need to know the account password to perform administrative operations.  Click install to begin the installation.

The installation process, including formatting the virtual disk, should begin.

After the installation is complete, before choosing to restart, right mouse on the CD icon at the bottom of the virtual machine window and choose "Remove disk from virtual drive" to avoid booting from the live CD again.

When the machine reboots, it should boot to the installed Ubuntu 10.04 EMC2 installation.

## Install Virtual Machine extensions ##
The Linux virtual machine functions significantly better with guest extensions installed.

"Devices->Install Guest Additions..."

Ubuntu should detect installed media.  Choose to autorun the media, and then choose to install the software.  You'll need to supply the administrative password to install the guest additions.

## Updating EMC2 ##
Since there are many fixes available to the current live CD version of EMC2 (2.4.3), updating is recommended.  The updated procedure can be found at:

http://buildbot.linuxcnc.org/

We are using Lucid (Ubuntu 10.4) "(32-bit only), realtime", and should update the 2.4 branch for now.  We are not running the pure simulation, but rather the real time system virtualized.  This will of course not really work for real time operations, but suits our purposes well.  Updating requires adding the following to the /etc/apt/sources.list.d/emc2-buildbot.list file (you'll need to edit the file using "sudo" as it is a system file):

```
deb     http://buildbot.linuxcnc.org/ lucid v2.4_branch-rt
deb-src http://buildbot.linuxcnc.org/ lucid v2.4_branch-rt
```

and then running:

```
sudo apt-get update
sudo apt-get install emc2
```

## Linux customizations ##
During install you hopefully chose to have the user logged in automatically.  It is also convenient and safer to have the screen saver not lock the machine and of course to not put the machine to sleep after an idle period of time.  This is done via:

1) Choosing "System->Preferences->Screen Saver", increasing the idle time to 30 minutes and un-checking the option to lock the screen.

2) You can then click the "Power Management" button and confirm that the machine will not be put to sleep when idle.

## Starting a machine simulation ##
You should now be ready to start playing with EMC2 in earnest.  In the base install there are several useful simulations.  A good starting point is the "axis" simulator.  You can see it home all axes automatically and get a good feel for the UI.  It is generally a good idea to choose "yes" when asked to copy the files to your home directory and create a desktop shortcut, as you can then more easily edit the configurations.

## Additional exercises ##
TODO: provide some steps to work through the basic simulator, using hal meter and hal scope to view values.