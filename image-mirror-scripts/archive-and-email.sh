./archive-images.sh > results.txt 2>&1
rc=$?
if [ ${rc} -eq 0 ]
then
  cat results.txt | mail -s "Sector67 web archive imaging: SUCCESS" scott@sector67.org team@sector67.org
else
  cat results.txt | mail -s "Sector67 web archive imaging: FAILED" scott@sector67.org team@sector67.org
fi
