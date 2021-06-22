h：
cd github\repo
dpkg-scanpackages.py debs --output Packages
"C:\Program Files\7-Zip\7zFM.exe" a -tbzip2 -r Packages.bz2 Packages