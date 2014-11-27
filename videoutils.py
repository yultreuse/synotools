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
    process = subprocess.Popen(['ffprobe','-loglevel','quiet','-show_streams','-of','json',mediaPath],stdout=subprocess.PIPE)
    dic = eval(process.stdout.read())
    process.stdout.close()
    return dic

def getFFProbeTags(mediaPath):
    process = subprocess.Popen(['ffprobe','-loglevel','quiet','-show_format','-of','json',mediaPath],stdout=subprocess.PIPE)
    dic = eval(process.stdout.read())
    process.stdout.close()
    parsedTags = {}
    tags = dic['format']['tags']
    
    # Parse album
    albumKeys = ['ALBUM','album']
    for k in albumKeys:
        if k in tags:
            parsedTags['album'] = tags[k].split(";")[0]
            break
            
    # Parse artist
    albumKeys = ['ARTIST','artist','album_artist']
    for k in albumKeys:
        if k in tags:
            parsedTags['artist'] = tags[k].split(";")[0]
            break
            
    # Parse Title
    albumKeys = ['TITLE','title']
    for k in albumKeys:
        if k in tags:
            parsedTags['title'] = tags[k].split(";")[0]
            break
            
    # Parse Date
    albumKeys = ['DATE','date']
    for k in albumKeys:
        if k in tags:
            parsedTags['date'] = tags[k].split(";")[0]
            break
            
    # Parse Genre
    albumKeys = ['GENRE','genre']
    for k in albumKeys:
        if k in tags:
            parsedTags['genre'] = tags[k].split(";")[0]
            break
        
    # Parse Date
    albumKeys = ['track']
    for k in albumKeys:
        if k in tags:
            parsedTags['track'] = "%02d" % int((tags[k].split(";")[0]).split("/")[0])
            break
        
    return parsedTags


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

