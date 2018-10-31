#Navigate to the addon directory
cd ~/.config/blender/2.79/scripts/addons/

#Create the zip archive in the home
rm ~/BakeMyScan.zip
zip -R ~/BakeMyScan.zip 'BakeMyScan/__init__.py' 'BakeMyScan/src/*.py' 'BakeMyScan/icons/*.png' 'BakeMyScan/scripts_meshlab/*.mlx'

#Go back to the previous directory
cd -
