#!/usr/bin/python
"""
Run DetectX Search
"""


import os
import sys
import subprocess
from distutils.version import LooseVersion
from CoreFoundation import CFPreferencesCopyAppValue


# Full path to DetectX Swift.app
DX = "/Applications/Utilities/DetectX Swift.app"
# Full path to output file for writing results
RESULTFILE = "/Library/Application Support/JAMF/Addons/DetectX/results.json"
# Minimum version of DetectX Swift
# nb: version 0.108 is required for single-user scanning
# version 0.110 is required for scanning all login users on the system
MINIMUM_VERSION = "0.110"
# Jamf policy custom trigger to run if DetectX is not found
JAMF_TRIGGER = "install_detectx"


def check_detectx_version():
    """Returns boolean whether or not the installed version of DetectX meets or
    exceeds the specified MINIMUM_VERSION"""
    result = False
    plist = os.path.join(DX, 'Contents/Info.plist')
    if os.path.exists(plist):
        installed_version = CFPreferencesCopyAppValue('CFBundleVersion', plist)
        if LooseVersion(installed_version) >= LooseVersion(MINIMUM_VERSION):
            result = True
    return result


def run_detectx_search():
    """Runs a DetectX Search"""
    # Ensure path to RESULTFILE exists
    if not os.path.exists(RESULTFILE):
        directory = os.path.dirname(RESULTFILE)
        if not os.path.exists(directory):
            os.makedirs(directory)
    # Run the DetectX search
    try:
        exe = os.path.join(DX, 'Contents/MacOS/DetectX Swift')
        cmd = [exe, 'search', '-aj', RESULTFILE]
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
        stdout, error = proc.communicate()
    except (IOError, OSError):
        pass
    return True if not proc.returncode == 0 else False


def run_jamf_policy(p):
    """Runs a jamf policy by id or event name"""
    cmd = ['/usr/local/bin/jamf', 'policy']
    if isinstance(p, basestring):
        cmd.extend(['-event', p])
    elif isinstance(p, int):
        cmd.extend(['-id', str(p)])
    else:
        raise TypeError('Policy identifier must be int or str')
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = proc.communicate()
    result_dict = {
        "stdout": out,
        "stderr": err,
        "status": proc.returncode,
        "success": True if proc.returncode == 0 else False
    }
    return result_dict


def main():
    """Main"""
    # Check if DetectX is installed at path 'DX'
    if not os.path.exists(DX):
        install_via_policy = run_jamf_policy(JAMF_TRIGGER)
        if not install_via_policy['success'] or not os.path.exists(DX):
            print ("DetectX was not found at path '{}' and could not be "
                   "installed via Jamf trigger '{}'".format(DX, JAMF_TRIGGER))
            sys.exit(1)
        else:
            print ("DetectX was installed via Jamf trigger "
                   "'{}'".format(JAMF_TRIGGER))
    # Check if installed DetectX meets minimum version requirement
    if not check_detectx_version():
        print ("The installed version of DetectX does not meet the "
               "minimum required version {}.".format(MINIMUM_VERSION))
        sys.exit(1)
    # Run DetectX Search
    detectx_search = run_detectx_search()
    if detectx_search:
        print "DetectX search complete."
        print "Results available at {}".format(RESULTFILE)
        sys.exit(0)
    else:
        print "An error occurred during the DetectX search."
        sys.exit(1)


if __name__ == '__main__':
    main()
