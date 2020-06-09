# uses ssh key pairs to login automatically
#
# last edited: 12/4/2014 by Scott Hasse
#
# run the archive process, removing server-side image files that are older than 15 days

ARCHIVE_DIR=./archive
SSH_KEY=~/.ssh/id_rsa
BW_LIMIT=0
ssh -i ${SSH_KEY} -o ServerAliveInterval=120 sector67camera@camera.sector67.org "./purge-older-than-two-weeks.sh"
