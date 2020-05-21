#recursively find and alter all mp4 files
#https://stackoverflow.com/questions/3964681/find-all-files-in-a-directory-with-extension-txt-in-python/3964690
#https://stackoverflow.com/questions/20042205/python-call-multiple-commands (see "Puffin GDI's answer")
import glob
import os
import subprocess

for root, dirs, files in os.walk(os.getcwd()):
    for file in files:
        if file.endswith(".mp4"):
            command = F'ffmpeg -i {file} -filter:v "setpts=0.25*PTS" -an output.mp4'
            cmd_str = F"cmd /k {command}"
            subprocess.Popen(cmd_str, cwd = root)            
            #print(os.path.join(root, file))
