import sys,subprocess

try:
    sys.argv[2]
    subprocess.call(F'ffmpeg -i {sys.argv[1]} -filter:v "setpts={float(sys.argv[2])}*PTS" -an {sys.argv[1]}spedup{str(int(float(sys.argv[2])**-1))}x.mp4')
except IndexError:
    subprocess.call(F'ffmpeg -i {sys.argv[1]} -filter:v "setpts=0.25*PTS" -an {sys.argv[1]}spedup4x.mp4')
