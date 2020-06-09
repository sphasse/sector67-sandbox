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

ARCHIVE_DIR=./archive
SSH_KEY=~/.ssh/id_rsa
BW_LIMIT=0
rsync -azu --stats --exclude logs -e "ssh -i ${SSH_KEY}" --bwlimit=${BW_LIMIT} sector67camera@camera.sector67.org:/home/sector67camera ${ARCHIVE_DIR}
