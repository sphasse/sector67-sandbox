

# Introduction #
designed for DNC drip feeding ("direct numeric control")
of CNC mill machines that talk via simple serial port data
transfer

# Details #
Developed by Scott Hasse for use at http://sector67.org

The script has been in use now for a couple of months without issue

Serial transfer adapted from http://pyserial.sourceforge.net/examples.html#miniterm
ProgressBar adapated from code at http://www.5dollarwhitebox.org/drupal/node/65 and
http://code.activestate.com/recipes/168639/

# TODO #
# Other enhancements as documented in the issues at http://code.google.com/p/sector67-sandbox/issues/list

# Downloading #
There are currently no releases.  Simply navigate to the source and download the latest version of the pydnc.py script.

# Running #
The script has been tested with Python 2.7.  You will need to download and install the pyserial extension (http://pyserial.sourceforge.net/).  Sample usage is provided by the script, but as an example:

```
python.exe -f -i c:\temp\my-part.M
```

Many options for the serial port are available as described in the script usage.  After starting the script, the file transfer will begin and can be paused by pressing any key.

# Issues #
Defects, feature requests, etc. should be logged at http://code.google.com/p/sector67-sandbox/issues/list, and given a tag of "Component-PythonSerialDNC".

# Contributing #
The source repository is an eclipse pydev project format.  Feel free to download and contribute.