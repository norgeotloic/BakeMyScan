import platform
import subprocess

def execute(cmd):
    #print("Running '" + cmd + "'")
    process  = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = process.communicate()
    code     = process.returncode
    if code:
        #"Error running '" + cmd + "'\n" + "OUTPUT:\n" + str(out) + "ERROR:\n" + str(err)
        raise Exception(code)

convertExe = "convert "
montageExe = "montage "
composeExe = "composite "

if platform.system() == "Windows":
    convertExe = "magick.exe convert "
    montageExe = "magick.exe montage "
    composeExe = "magick.exe composite "

mmgsExe = "mmgs_O3 " if (platform.system() == "Linux" or platform.system() == "Darwin") else None

try:
    execute(convertExe + "-version")
except:
    convertExe = None

try:
    execute(montageExe + "-version")
except:
    montageExe = None

try:
    execute(composeExe + "-version")
except:
    composeExe = None

try:
    execute("which " + mmgsExe)
except:
    mmgsExe = None

#print(convertExe, composeExe, montageExe, mmgsExe)
