#!/usr/bin/python

import sys
import os
from videoutils import *

RootZikPath = "/media/DiskStation/music"
FlacZikPath = RootZikPath + ""

def main(pattern):

    def processOneDir(path,d):
        flacDir = os.path.normpath(path)
        _,tail = os.path.split(flacDir)
        mp3Dir = os.path.join(os.curdir,tail)

        print "will transcode files of %s to %s " % (flacDir,mp3Dir)
        for inRoot,dirs,files in os.walk(flacDir):
            outRoot = os.path.normpath(os.path.join(mp3Dir,os.path.relpath(inRoot,flacDir)))
            for flac in files:
                if flac.endswith("flac"):
                    inputFile  = os.path.join(inRoot,flac)
                    
                    # Build output file name            
                    outputFile = ""
                    tags = getFFProbeTags(inputFile)
                    if 'artist' in tags and 'title' in tags:
                        if 'track' in tags:
                            outputFile = tags['artist'] + " - " + tags['track'] + " - " + tags['title'] + ".mp3"
                        else:
                            outputFile = tags['artist'] + " - " + tags['title'] + ".mp3"
                    else:                       
                        outputFile =  os.path.join(outRoot,flac.rstrip("flac") + "mp3")
                        
                    # Build output directory
                    outputDir = ""
                    if 'artist' in tags:
                        outputDir = tags['artist']
                        if not os.path.isdir(outputDir):
                            os.mkdir(outputDir)
                        if 'album' in tags:
                            if 'date' in tags:
                                newDir = tags['date'] + " - " + tags['album']
                            else:
                                newDir = tags['album']
                            outputDir = os.path.join(outputDir,newDir)
                            if not os.path.isdir(outputDir):
                                os.mkdir(outputDir)
                                
                    if outputDir is not "":
                        outputFile = os.path.join(outputDir,outputFile)
                        
                                        
                    # Grab first video stream & first audio stream
                    dico = getFFProbeDic(inputFile)
                    videoStream = None
                    for stream in dico['streams']:
                        if stream['codec_type'] == 'video':
                            videoStream = stream
                            break
                    
                    vidOpt = ""
                    if videoStream is not None:                        
                        vidOpt = "-c:v mjpeg -vsync 2 -pix_fmt yuvj420p"
                        width = int(videoStream['width'])
                        height = int(videoStream['height'])
                        if width>400 or height>400:
                            if width>height:
                                vidOpt += " -vf scale=400:-1"
                            else:
                                vidOpt += " -vf scale=-1:400"
                    else:
                        vidOpt = "-vn"
                                
                    audOpt = "-b:a 192k -sample_fmt s16p -id3v2_version 3 -ar 44100 -map_metadata -1"
                    for t,v in tags.iteritems():
                        audOpt += " -metadata " + t + "='" + v + "'"                                      
                    
                    d[inputFile] = (outputFile,vidOpt,audOpt)

    candidates = []
    for root,dirs,names in os.walk(FlacZikPath):
        for rep in dirs:
            if pattern in rep:
                path = os.path.join(root,rep)
                candidates.append(path)    

    todo = {}
    if len(candidates)==0:
        print "Warning : " + pattern + " was not found in " + FlacZikPath
    else:        
        for path in candidates:
	           processOneDir(path,todo)

    for flac,(mp3,vidOpt,audOpt) in todo.iteritems():
        print "handling " + flac
        command = 'ffmpeg -y -loglevel quiet -i "' + flac + '" ' + vidOpt + ' ' + audOpt + ' "' + mp3 + '"'        
        os.system(command)


if __name__ == "__main__":
    main(sys.argv[1]) 
