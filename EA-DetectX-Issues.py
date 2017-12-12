#!/usr/bin/python
"""
Read DetectX Results and report any discovered issues

Results:
'' (empty string): RESULTFILE was not found or not readable. Implies a search
                   has not yet been run, or the results were invalid JSON.
'None': The DetectX search was run, but did not find any issues.
(list): A list of detected issues (file paths)
"""


import os
import json


# Path to DetectX Result file
RESULTFILE = '/Library/Application Support/JAMF/Addons/DetectX/results.json'


def decode_results(path):
    """Decodes the JSON object at path 'path' and returns a list of discovered
    issues"""
    issues = []
    try:
        with open(path, 'r') as data:
            try:
                results = json.load(data)
                issues = results['issues']
            except (KeyError, ValueError):
                pass
    except (OSError, IOError):
        pass
    return issues


def main():
    """Main"""
    if os.path.exists(RESULTFILE):
        issues = decode_results(RESULTFILE)
        if len(issues) > 0:
            EA = '\n'.join(issues)
        else:
            EA = 'None'
    else:
        EA = ''
    print '<result>%s</result>' % EA


if __name__ == '__main__':
    main()
