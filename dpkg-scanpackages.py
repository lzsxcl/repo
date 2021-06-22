# Copyright 2018 Raymond Velasquez

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Script: dpkg-scanpackages.py
# Author: Raymond Velasquez <at.supermamon@gmail.com>

script_name    = 'dpkg-scanpackages.py'
script_version = '0.4.1'

import glob, sys, os, argparse
from pydpkg import Dpkg

class DpkgInfo:
    def __init__(self,binary_path):
        self.binary_path = binary_path
        self.headers = {}
        pkg = Dpkg(self.binary_path)

        # build the information for the apt repo
        self.headers = pkg.headers
        self.headers['Filename'] = pkg.filename.replace("\\",'/')
        self.headers['Size'] = pkg.filesize
        self.headers['MD5sum'] = pkg.md5
        self.headers['SHA1'] = pkg.sha1
        self.headers['SHA256'] = pkg.sha256

    def __str__(self):
        pretty = ''
        keyOrder=[
            'Package','Version','Architecture','Maintainer',
            'Depends','Conflicts','Breaks','Replaces',
            'Filename','Size',
            'MD5sum','SHA1','SHA256',
            'Section','Description'
        ]
        # add as per key order
        for key in keyOrder:
            if key in self.headers:
                pretty = pretty + ('{0}: {1}\n').format(key,self.headers[key])

        # add the rest alphabetically
        for key in sorted(self.headers.keys()):
            if not key in keyOrder:
                pretty = pretty + ('{0}: {1}\n').format(key,self.headers[key])
        return pretty

class DpkgScanpackages:
    def __init__(self,binary_path, multiversion=None,packageType=None,arch=None,output=None):
        self.binary_path = binary_path

        # throw an error if it's an invalid path
        if not os.path.isdir(self.binary_path):
            raise ValueError('binary path {0} not found'.format(self.binary_path))

        # options
        self.multiversion = multiversion if multiversion is not None else False
        self.packageType = packageType if packageType is not None else 'deb'
        self.arch = arch
        self.output = output

        self.packageList = []

    def __get_packages(self):
        # get all files
        files = glob.glob( os.path.join(self.binary_path,"") + "*" + self.packageType )
        for fname in files:
            # extract the package information
            pkg_info = DpkgInfo(fname)

            # if arch is defined and does not match package, move on to the next
            if self.arch is not None:
                if str(pkg_info.headers['Architecture']) != self.arch:
                    continue

            # if --multiversion switch is passed, append to the list
            if self.multiversion==True:
                self.packageList.append(pkg_info)
            else:
                # finf if package is already in the list
                matchedItems = [(index,pkg) for (index,pkg) in enumerate(self.packageList) if self.packageList and pkg.headers['Package'] == pkg_info.headers['Package']]
                if len(matchedItems)==0:
                    # add if not
                    self.packageList.append(pkg_info)
                else:
                    # compare versions and add if newer
                    matchedIndex = matchedItems[0][0]
                    matchedItem = matchedItems[0][1]

                    dpkg = Dpkg(pkg_info.headers['Filename'])
                    if dpkg.compare_version_with(matchedItem.headers['Version']) == 1:
                        self.packageList[matchedIndex] = pkg_info

    def scan(self,returnList=False):
        self.__get_packages()
        if (returnList):
            return (self.packageList)
        else:
            if not self.output is None:
                file = open(self.output, "wb")

            for p in self.packageList:
                if self.output is None:
                    print(str(p))
                else:
                    file.write(bytes(str(p),'utf-8'))
                    file.write(bytes("\n",'utf-8'))
            if not self.output is None:
                file.close()


def print_error(msg):
    COLOR_RED   = '\033[91m'
    COLOR_RESET = "\033[0;0m"
    COLOR_BOLD  = '\033[1m'
    print('{0}:{1}{2} error{3}: {4}'.format(script_name,COLOR_RED,COLOR_BOLD,COLOR_RESET,msg))
    print('')
    print('Use --help for program usage information.')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--version',
                        action='version',
                        version='Debian %(prog)s version '+script_version+'.',
                        help='show the version.')
    parser.add_argument('-m','--multiversion',
                        default=False,
                        action="store_true",
                        dest='multiversion',
                        help='allow multiple versions of a single package.')
    parser.add_argument('-a','--arch',
                        default=None,
                        action="store",
                        dest='arch',
                        help='architecture to scan for.')
    parser.add_argument('-t','--type',
                        default='deb',
                        action="store",
                        dest='type',
                        help='scan for <type> packages (default is \'deb\').')
    parser.add_argument('-o','--output',
                        action="store",
                        dest='output',
                        help='Write to file instead of stdout')
    parser.add_argument('binary_path')

    args = parser.parse_args()
    try:
        DpkgScanpackages(
            binary_path=args.binary_path,
            multiversion=args.multiversion,
            arch=args.arch,
            packageType=args.type,
            output=args.output
        ).scan()
    except ValueError as err:
        print_error(err.message)

if __name__ == "__main__":
    main()