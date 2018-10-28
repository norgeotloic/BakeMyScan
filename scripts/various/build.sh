#Navigate to the addon directory
cd $1
cd ..

#Create the zip archive in the home
rm ~/BakeMyScan.zip
zip -R ~/BakeMyScan.zip 'BakeMyScan/__init__.py' 'BakeMyScan/src/*.py' 'BakeMyScan/icons/*.png' 'BakeMyScan/scripts_meshlab/*.mlx'
