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

thumbSpec = {}
thumbSpec['XL'] = ("SYNOPHOTO_THUMB_XL.jpg","1280","min")
thumbSpec['M'] = ("SYNOPHOTO_THUMB_M.jpg","320","min")
thumbSpec['PREVIEW'] = ("SYNOPHOTO_THUMB_PREVIEW.jpg","256","max")

eaDir = '@eaDir'

operators = {}
operators['min'] = 'gt'
operators['max'] = 'lt'

picExts = ['.jpg','.JPG','.jpeg','.JPEG','.png','.PNG','.bmp','.BMP','.tif','.TIF']

red = '\033[0;31m'
nc = '\033[0m'

def makePicThumbs(imagePath,loglevel,forceupdate):
    picDir,picName = os.path.split(imagePath)
    thumbsDir = os.path.join(picDir,eaDir)
    if not os.path.isdir(thumbsDir):
        os.mkdir(thumbsDir)
    curPicThumbsDir = os.path.join(thumbsDir,picName)
    if forceupdate:
        if os.path.isdir(curPicThumbsDir):
            shutil.rmtree(curPicThumbsDir)
    if not os.path.isdir(curPicThumbsDir):
        os.mkdir(curPicThumbsDir)
        
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
            
def walkMediaDir(dir,loglevel,forceupdate):
    for root,dirs,names in os.walk(dir):
        for filename in names:
            picPath = os.path.join(root,filename)
            if eaDir not in picPath:
                base,ext = os.path.splitext(filename)
                if ext in picExts :
                    print 'handling ' + picPath
                    makePicThumbs(picPath,loglevel,forceupdate)
            
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate thumbnails for DS photo 6')
    parser.add_argument("FOLDER",help="FOLDER is a valid directory path containing photo to index")
    parser.add_argument("-l","--loglevel",help="Specify ffmpeg loglevel from quiet|panic|fatal|error|warning|info|verbose")
    parser.add_argument("-f","--force-update",action="store_true",help="force creation of thumbnails : erase previous thumbs if any")
    args = vars(parser.parse_args())

    if args['loglevel'] is None:
        args['loglevel'] = 'quiet'
    
    walkMediaDir(args['FOLDER'],args['loglevel'],args['force_update'])
    