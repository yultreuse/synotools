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

thumbSpec = {}
thumbSpec['XL'] = ("SYNOPHOTO_THUMB_XL.jpg","1280","min")
thumbSpec['M'] = ("SYNOPHOTO_THUMB_M.jpg","320","min")
thumbSpec['PREVIEW'] = ("SYNOPHOTO_THUMB_PREVIEW.jpg","256","max")

eaDir = '@eaDir'

operators = {}
operators['min'] = 'gt'
operators['max'] = 'lt'

picExts = ['.jpg','.JPG','.jpeg','.JPEG','.png','.PNG','.bmp','.BMP','.tif','.TIF']

def makePicThumbs(imagePath):
    picDir,picName = os.path.split(imagePath)
    thumbsDir = os.path.join(picDir,eaDir)
    if not os.path.isdir(thumbsDir):
        os.mkdir(thumbsDir)
    curPicThumbsDir = os.path.join(thumbsDir,picName)
    if not os.path.isdir(curPicThumbsDir):
        os.mkdir(curPicThumbsDir)
        
    for name,size,spec in thumbSpec.itervalues():
        thumbPath = os.path.join(curPicThumbsDir,name)
        if not os.path.exists(thumbPath):
            vfilter = "\"scale='if(lt(iw,%s)*lt(ih,%s),-1,if(%s(iw,ih),-1,%s))':'if(lt(iw,%s)*lt(ih,%s),-1,if(%s(iw,ih),%s,-1))'\"" % (size,size,operators[spec],size,size,size,operators[spec],size)
            inArgs = "-loglevel quiet -y -i '" + imagePath + "'"
            outArgs = "-vf " + vfilter + " '" + thumbPath + "'"
            os.system("ffmpeg " + inArgs + " " + outArgs)
            print thumbPath + " created"
            
def walkMediaDir(dir):
    for root,dirs,names in os.walk(dir):
        for filename in names:
            if eaDir not in filename:
                base,ext = os.path.splitext(filename)
                if ext in picExts :
                    picPath = os.path.join(root,filename)
                    print 'handling ' + picPath
                    makePicThumbs(picPath)
            
if __name__ == "__main__":
    walkMediaDir(sys.argv[1])