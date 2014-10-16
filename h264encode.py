#!/usr/bin/python
'''
Author : Julien MOTTIN
License : GNU GPL3
Use : 
    Convert videos to h264 / AAC with same quality

Dependencies : ffmpeg modern build, with many codecs...
version : 0.1
'''
import sys
import os
import argparse
import shutil
import stat
import subprocess

picExts = ['.jpg','.JPG','.jpeg','.JPEG','.png','.PNG','.bmp','.BMP','.tif','.TIF']
movExts = ['.mov','.MOV','.avi','.AVI','.mts','.MTS','.mp4','.MP4','.mpg','.MPG','.mpeg','.MPEG','.mkv','.MKV']

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

def getFFProbeDic(mediaPath):
    process = subprocess.Popen(['ffprobe','-loglevel','quiet','-show_streams','-of','json',mediaPath],stdout=subprocess.PIPE)
    dic = eval(process.stdout.read())
    process.stdout.close()
    return dic           

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Convert video to h264 / aac for compatible use with chromecast')
    parser.add_argument("INPUT",help="INPUT is the source video file to convert")
    parser.add_argument("-l","--loglevel",help="Specify ffmpeg loglevel from quiet|panic|fatal|error|warning|info|verbose")
    parser.add_argument("-d","--delete-source",action="store_true",help="remove INPUT after successful transcode")
    args = vars(parser.parse_args())
    
    if args['loglevel'] is None:
        args['loglevel'] = 'error'
    
    inDic = getFFProbeDic(args['INPUT'])
    inDir,inName = os.path.split(args['INPUT'])
    inBase,inExt = os.path.splitext(inName)
    if len(inDic['streams'])>2:
        print yellow + "Warning : input file has more than 2 streams" + nc

    # Grab first video stream & first audio stream
    videoStream = None
    for stream in inDic['streams']:
        if stream['codec_type'] == 'video':
            videoStream = stream
            break    
    audioStream = None
    for stream in inDic['streams']:
        if stream['codec_type'] == 'audio':
            audioStream = stream
            break

    if videoStream is not None and audioStream is not None:

        # First check if transcode required
        if videoStream['codec_name']=='h264' and audioStream['codec_name']=='aac':
            print "INPUT already in h264 / aac not doing anything"

        else:
            # Build output path
            outFileName = inBase + "-h264.mp4"
            outFilePath = os.path.join(inDir,outFileName)
            targetAudBR = min(int(audioStream['bit_rate']),128000)
            audOpt = "-c:a libfaac -b:a %d -ac 2 -ar 48000" % targetAudBR
            inArgs = "-y -loglevel %s -i '%s'" % (args['loglevel'],args['INPUT'])

            # If only audio transcode needed
            if videoStream['codec_name']=='h264':
                vidOpt = "-c:v copy"
                os.system("ffmpeg " + inArgs + " " + vidOpt + " " + audOpt + " '" + outFilePath + "'")

            # Video transcoding needed, re-encode whole video
            else:
                targetVidBR = min(int(videoStream['bit_rate']),youtubeVideoBitrate(videoStream['height']))
                vidOpt = "-f mp4 -c:v libx264 -preset fast -b:v " + str(targetVidBR)
                os.system("ffmpeg " + inArgs + " " + vidOpt + " " + audOpt + " -pass 1 /dev/null && ffmpeg " + inArgs + " " + vidOpt + " " + audOpt + " -pass 2 '" + outFilePath + "'")
                
            if os.path.isfile(outFilePath):
                print outFilePath + " created"
                if args['delete_source']:
                    os.remove(args['INPUT'])
            else:
                print red + "ERROR while creating " + outFilePath + nc


    else:
        print red + "Fail to locate suitable streams in input file" + nc

