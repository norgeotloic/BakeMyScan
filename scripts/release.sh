rm ~/BakeMyScan.zip
rm ~/bakemyscan.xml
rm -rf ~/BakeMyScan_bk

#Navigate to the addon directory
cd ~/.config/blender/2.79/scripts/addons/

#Theme
cp ~/.config/blender/2.79/scripts/presets/interface_theme/bakemyscan.xml ~/bakemyscan.xml
#Backup
cp -r BakeMyScan/ ~/BakeMyScan_bk
#Zip the meaningful files
zip -R ~/BakeMyScan.zip 'BakeMyScan/__init__.py' 'BakeMyScan/src/*.py' 'BakeMyScan/icons/*.png' 'BakeMyScan/scripts_meshlab/*.mlx' 'BakeMyScan/README.md' 'BakeMyScan/LICENSE' 'BakeMyScan/scripts/*.py' 'BakeMyScan/tests/*'

#Go back to the initial directory
cd -
