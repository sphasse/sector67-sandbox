#!/bin/bash

# a script to initiate the image archive process, mirror the images to a secondary disk, and remove the images from the web server past a certain date

# create a function to prefix output
prefixoutput() {
  while IFS= read -r line; do
    echo "$SCRIPT $(date) $line"
  done
}

# if anything goes wrong, exit before removing files
set -u -o pipefail

SCRIPT=initial-storage
echo "reading current space used..."
./get-storage-size.sh | prefixoutput
rc=$?
if [ ${rc} -eq 0 ]
then
  echo "completed successfully"
else
  echo "did not complete successfully, return code ${rc}"
  exit 1
fi

SCRIPT=download
echo "syncing images from the web server..."
./sync-from-web.sh | prefixoutput
rc=$?
if [ ${rc} -eq 0 ]
then
  echo "completed successfully"
elif [ ${rc} -eq 24 ]
then
  echo "completed with warnings, return code ${rc}"
  echo "continuing"
else
  echo "did not complete successfully, return code ${rc}"
  exit 1
fi

SCRIPT=mirror
echo "syncing images to a mirror drive"
./sync-to-mirror-drive.sh | prefixoutput
rc=$?
if [ ${rc} -eq 0 ]
then
  echo "completed successfully"
else
  echo "did not complete successfully, return code ${rc}"
  exit 1
fi

SCRIPT=delete
echo "removing old server-side files"
./remove-old-server-side-files.sh | prefixoutput
rc=$?
if [ ${rc} -eq 0 ]
then
  echo "completed successfully"
else
  echo "did not complete successfully, return code ${rc}"
  exit 1
fi

SCRIPT=final-storage
echo "reading final space used..."
./get-storage-size.sh | prefixoutput
rc=$?
if [ ${rc} -eq 0 ]
then
  echo "completed successfully"
else
  echo "did not complete successfully, return code ${rc}"
  exit 1
fi
