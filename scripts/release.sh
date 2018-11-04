#Create the zip archive in the home
rm ~/BakeMyScan.zip
rm ~/bakemyscan.xml

#Navigate to the addon directory
cd ~/.config/blender/2.79/scripts/addons/

#Copy the preferences to the folder
cp BakeMyScan/bakemyscan.xml ~/bakemyscan.xml

#Zip the meaningful files
zip -R ~/BakeMyScan.zip 'BakeMyScan/__init__.py' 'BakeMyScan/src/*.py' 'BakeMyScan/icons/*.png' 'BakeMyScan/scripts_meshlab/*.mlx' 'BakeMyScan/README.md' 'BakeMyScan/LICENSE' 'BakeMyScan/scripts/*.py' 'BakeMyScan/tests/*'

#Go back to the initial directory
cd -
