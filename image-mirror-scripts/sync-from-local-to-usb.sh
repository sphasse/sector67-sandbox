# sync.sh
#
# rsync tool to sync images 
# from camera.sector67.org
# to the local machine
#
# uses ssh key pairs to login automatically
#
# last edited: 12/4/2014 by Scott Hasse
#
# * download only those files on [server name] in [server target directory]
# that are newer than what is already on the notebook PC
# * limit bandwidth for the transfers

rsync -avzu /cygdrive/e/camera-archive/archive/sector67camera /cygdrive/g/Meyer_10513942_96234295_SN_Data/Complete/camera-archive/archive
