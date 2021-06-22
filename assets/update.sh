#!/bin/bash

echo

./clean.sh

echo
echo "Rebuilding package list..."
echo "--------------------------"

rm -f Packages*
dpkg-scanpackages -m ./debs /dev/null > Packages
bzip2 -k Packages
./dpkg-scanpackages -m ./debians/ /dev/null > Packages

echo "--------------------------"
echo "Done."
echo
