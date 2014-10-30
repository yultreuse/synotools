'''
Author : Julien MOTTIN
License : GNU GPL3
Use : 
    Shared utilies for video transcoding

Dependencies : ffmpeg modern build, with many codecs...
version : 0.1
'''

import subprocess
import os

def getFFProbeDic(mediaPath):
    process = subprocess.Popen(['ffprobe','-loglevel','quiet','-show_streams','-show_format','-of','json',mediaPath],stdout=subprocess.PIPE)
    dic = eval(process.stdout.read())
    process.stdout.close()
    return dic

red = '\033[0;31m'
yellow = '\033[0;33m'
nc = '\033[0m'

def youtubeVideoBitrate(height):
    h = int(height)
    out = int(-3.85*h*h+15240*h-3965000)
    
    # Forbid too low bitrates
    if out<300000:
        out = 300000
        
    return out

def cleanFFMpeg2PassFiles(passLogFile="ffmpeg2pass"):
    pattern = passLogFile + "*"
    os.system("rm -f " + pattern)

