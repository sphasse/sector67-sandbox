# sync.sh
#
# rsync tool to mirror to the backup drive
# from camera.sector67.org
# to the local machine
#
# last edited: 5/10/2019 by Scott Hasse
#

rsync -azu --stats ../camera-archive/ ../../SECTOR67-B/camera-archive/
