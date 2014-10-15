#!/usr/bin/python
'''
Author : Julien MOTTIN
License : GNU GPL3
Use : 
    Generate thumbnails for synology DS photo 6
    Prerequisite : mount photo volumes in NFS on the machine you want
    this script to be executed.
    Launch the script doing so : $ ./synoThumbs /path/to/photo/folder

Dependencies : ffmpeg modern build, with many codecs...
version : 0.1
'''
import sys
import os
import argparse
import shutil
import stat
import subprocess

thumbSpec = {}
thumbSpec['XL'] = ("SYNOPHOTO_THUMB_XL.jpg","1280","min")
thumbSpec['M'] = ("SYNOPHOTO_THUMB_M.jpg","320","min")
thumbSpec['PREVIEW'] = ("SYNOPHOTO_THUMB_PREVIEW.jpg","256","max")

vidSpec = {}
vidSpec['FLV']  = ("SYNOPHOTO_FILM.flv","480","-c:a libfaac -b:a 96k -ar 48000","-c:v libx264 -preset faster")
vidSpec['MP4']  = ("SYNOPHOTO_FILM_CONVERT_MPEG4.mp4","360","-c:a libfaac -b:a 96k -ar 48000","-c:v mpeg4 -q:v 16")
vidSpec['H264']  = ("SYNOPHOTO_FILM_H264.mp4","-1","-c:a libfaac -b:a 128k -ar 48000","-c:v libx264 -preset faster -crf 24")

eaDir = '@eaDir'

operators = {}
operators['min'] = 'gt'
operators['max'] = 'lt'

picExts = ['.jpg','.JPG','.jpeg','.JPEG','.png','.PNG','.bmp','.BMP','.tif','.TIF']
movExts = ['.mov','.MOV','.avi','.AVI','.mts','.MTS','.mp4','.MP4','.mpg','.MPG','.mpeg','.MPEG']

red = '\033[0;31m'
nc = '\033[0m'

def getFFProbeDic(mediaPath):
    process = subprocess.Popen(['ffprobe','-loglevel','quiet','-show_streams','-of','json',mediaPath],stdout=subprocess.PIPE)
    dic = eval(process.stdout.read())
    process.stdout.close()
    return dic

def makePicThumbs(imagePath,curPicThumbsDir,loglevel):        
    for name,size,spec in thumbSpec.itervalues():
        thumbPath = os.path.join(curPicThumbsDir,name)
        if not os.path.exists(thumbPath):
            vfilter = "\"scale='if(lt(iw,%s)*lt(ih,%s),-1,if(%s(iw,ih),-1,%s))':'if(lt(iw,%s)*lt(ih,%s),-1,if(%s(iw,ih),%s,-1))'\"" % (size,size,operators[spec],size,size,size,operators[spec],size)
            inArgs = "-loglevel %s -y -f image2 -i '%s'" % (loglevel,imagePath)
            outArgs = "-vf " + vfilter + " '" + thumbPath + "'"
            os.system("ffmpeg " + inArgs + " " + outArgs)
            if os.path.isfile(thumbPath):
                os.chmod(thumbPath, stat.S_IRWXU | stat.S_IRWXO | stat.S_IRWXG)
                print thumbPath + " created"
            else:
                print red + "ERROR while creating " + thumbPath + nc

def makeMovThumbs(movPath,curMovThumbsDir,loglevel):
    
    # Grab 1st Video & Audio streams
    mediaDic = getFFProbeDic(movPath)
    videoStream = None
    for stream in mediaDic['streams']:
        if stream['codec_type'] == 'video':
            videoStream = stream
            break    
    audioStream = None
    for stream in mediaDic['streams']:
        if stream['codec_type'] == 'audio':
            audioStream = stream
            break
        
    # Make thumbnails
    for k,(name,size,spec) in thumbSpec.iteritems(): 
        if k in ['M','XL']:
            thumbPath = os.path.join(curMovThumbsDir,name)
            if not os.path.exists(thumbPath):
                vfilter = "\"scale='min(ih,%s)*dar':'min(ih,%s)':1\"" % (size,size)
                seekStart = str(float(videoStream['duration'])/3)
                inArgs = "-loglevel %s -y -ss %s -i '%s'" % (loglevel,seekStart,movPath)
                outArgs = "-an -vframes 1 -vf " + vfilter + " '" + thumbPath + "'"
                os.system("ffmpeg " + inArgs + " " + outArgs)
                if os.path.isfile(thumbPath):
                    os.chmod(thumbPath, stat.S_IRWXU | stat.S_IRWXO | stat.S_IRWXG)
                    print thumbPath + " created"
                else:
                    print red + "ERROR while creating " + thumbPath + nc

    # Make video thumbnails
    for k,(name,size,aspec,vspec) in vidSpec.iteritems():
        # for all but H264
        thumbPath = os.path.join(curMovThumbsDir,name)
        if not os.path.exists(thumbPath):
            
             # don't transcode to H264 if already at the correct codec
            if videoStream['codec_name']=='h264' and k=='H264':
                _,basename = os.path.split(curMovThumbsDir)
                os.symlink(os.path.join('../..',basename), os.path.join(curMovThumbsDir,name))
                print thumbPath + " created"
            
            else:    
                vfilter = "\"scale='if(gcd(%s*dar,2),%s*dar-1,%s*dar)':%s:1\"" % (size,size,size,size)
                inArgs = "-loglevel %s -y -i '%s'" % (loglevel,movPath)
                outArgs = aspec + " " + vspec + " -vf " + vfilter + " '" + thumbPath + "'"
                os.system("ffmpeg " + inArgs + " " + outArgs)
                
                if os.path.isfile(thumbPath):
                    os.chmod(thumbPath, stat.S_IRWXU | stat.S_IRWXO | stat.S_IRWXG)
                    print thumbPath + " created"
                else:
                    print red + "ERROR while creating " + thumbPath + nc

            
def walkMediaDir(dir,loglevel,forceupdate,forcevideoupdate):
    for root,dirs,names in os.walk(dir):
        for filename in names:
            mediaPath = os.path.join(root,filename)
            if eaDir not in mediaPath:
                base,ext = os.path.splitext(filename)
                if ext in picExts + movExts :
                    print 'handling ' + mediaPath
                    
                    # Build @eadir and @eadir/mediaName folders
                    mediaDir,mediaName = os.path.split(mediaPath)
                    thumbsDir = os.path.join(mediaDir,eaDir)
                    if not os.path.isdir(thumbsDir):
                        os.mkdir(thumbsDir)
                    curPicThumbsDir = os.path.join(thumbsDir,mediaName)
                    
                    # Check force update option seperatly for movies & images
                    if (ext in picExts and forceupdate) or (ext in movExts and forcevideoupdate):
                            if os.path.isdir(curPicThumbsDir):
                                shutil.rmtree(curPicThumbsDir)
                    
                    # Create media thumb dir if needed
                    if not os.path.isdir(curPicThumbsDir):
                        os.mkdir(curPicThumbsDir)
                    
                    # Call indexer
                    if ext in picExts:
                        makePicThumbs(mediaPath,curPicThumbsDir,loglevel)
                    
                    if ext in movExts:
                        makeMovThumbs(mediaPath,curPicThumbsDir,loglevel)
            

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate thumbnails for DS photo 6')
    parser.add_argument("FOLDER",help="FOLDER is a valid directory path containing photo to index")
    parser.add_argument("-l","--loglevel",help="Specify ffmpeg loglevel from quiet|panic|fatal|error|warning|info|verbose")
    parser.add_argument("-f","--force-update",action="store_true",help="force creation of thumbnails (bit slow): erase previous thumbs if any")
    parser.add_argument("-fv","--force-video-update",action="store_true",help="force creation of thumbnails for movies (more slow) : erase previous thumbs if any")
    args = vars(parser.parse_args())
    
    if args['loglevel'] is None:
        args['loglevel'] = 'error'
    
    walkMediaDir(args['FOLDER'],args['loglevel'],args['force_update'],args['force_video_update'])
