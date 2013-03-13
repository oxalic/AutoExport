#!/usr/bin/env python

import sys
import os
import random
import time
from lxml import etree
import shutil
from svgfig import *


# Config Variables
#==================
#Controls the resolution(dpi) of exported bitmaps:
res = 300
#Controls the prefix of groups that will become images in the svg file also can be a list
prefixes = ['img:', 'cmp:']

# I took this from "http://stackoverflow.com/questions/2359317/how-to-find-elements-by-id-field-in-svg-file-using-python"
# however it can be found simply by looking at the svg file, ignoring the base xmlns = w3c line
# and removing the xmlns prefix from all other lines, and quoting the stuff on the left side of the equals sign

nsmap = {
    'sodipodi': 'http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd',
    'cc': 'http://web.resource.org/cc/',
    'svg': 'http://www.w3.org/2000/svg',
    'dc': 'http://purl.org/dc/elements/1.1/',
    'xlink': 'http://www.w3.org/1999/xlink',
    'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
    'inkscape': 'http://www.inkscape.org/namespaces/inkscape'
    }
    
# This is taken from a basic plain svg file (made in inkscape)
# with something like the width and height removed, not sure if that 
# was necessary now that we're running it through inkscape and changing the 
# canvas size with verbs
wrapperBegin = """
<svg
   xmlns:dc="http://purl.org/dc/elements/1.1/"
   xmlns:cc="http://creativecommons.org/ns#"
   xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
   xmlns:svg="http://www.w3.org/2000/svg"
   xmlns="http://www.w3.org/2000/svg"
   version="1.1">
  <defs
     id="defs4059" />
  <metadata
     id="metadata4062">
    <rdf:RDF>
      <cc:Work
         rdf:about="">
        <dc:format>image/svg+xml</dc:format>
        <dc:type
           rdf:resource="http://purl.org/dc/dcmitype/StillImage" />
        <dc:title></dc:title>
      </cc:Work>
    </rdf:RDF>
  </metadata>
"""

wrapperEnd = """
</svg>"""


def getImgs(svg):
    # get a list of elements which are a group
    # print 'getImgs called!'
    allGroups = svg.xpath('//svg:g', namespaces=nsmap)
    
    # If a group has an id that begins with one of the prefixes then add it's id tag contents to the list of ids
    #     and its element to the list of elements
    
    # first set the ids and elements lists to null
    ids = []
    elements = []
    
    # for each group check if it's id is prepended by each of the prefixes, and if so add it to both lists
    for group in allGroups:
        identity = group.get("id")
        for pref in prefixes:
            length = len(pref)
            if identity[0:length] == pref:
                ids.append(identity)
                elements.append(group)
            
    #return a list of tuples, first element being the id, second element being the element pointer
    tupleList = zip(* [ids, elements])
    return tupleList
    

def svgExport(elem, name):
    # wrap the textual representation of the element in the beginning wrapper and the ending wrapper
    svgtext = wrapperBegin + etree.tostring(elem, encoding='UTF-8', method="xml") + wrapperEnd
    fileName = name + ".svg"
    open(fileName,"w").write(svgtext)
    
    #ugh this seems to be the only way that I can do this for now, repeatedly opens and closes inkscape though:
    # http://www.inkscapeforum.com/viewtopic.php?f=29&t=6095
    os.system('inkscape --verb=FitCanvasToSelectionOrDrawing --verb=FileSave --verb=FileClose %s' % (fileName))


def batchExport(type, file, tupleLists):
    # A list of accepted type arguments
    types = ['png', 'svg', 'eps']
    
    # if exporting all types, then export each type for each tuple in the list
    for tuple in tupleLists:
        if type == 'all':
            for curType in types:
                export(curType, file, tuple)
        # Otherwise, just loop over the tuple list and export each type
        else:
            export(type, file, id)
            

def export(type, file, idTuple):
    # Set id (full text of id tag)
    id = idTuple[0]
    
    # set name (id tag minus prefix)
    for pref in prefixes:
        length = len(pref)
        if idTuple[0][0:length] == pref:
            name = idTuple[0][len(pref):]
            break
            
    # set elem, the pointer to the elementtree object
    elem = idTuple[1]
    
    # 'png' and 'eps' are exported similarly
    if (type == 'png') or (type == 'eps'):
        print 'Exporting %s.%s from %s' % (name, type, file)
        os.system('inkscape --export-dpi=%s --export-area-snap --export-id=%s --export-%s=%s.%s --file=%s' % (res, id, type, name, type, file))
    
    # 'svg's have to be done vastly differently
    if type == 'svg':
        svgExport(elem, name)


if __name__ == '__main__':
   
    # Check the calling and make sure that it is proper 
    inputFile = sys.argv[1]
    exportType = sys.argv[2]  
    acceptedTypes = ['svg', 'eps', 'png', 'all']

    if (len(sys.argv) != 3):  # this is three because I usually call it via "python file.svg all"
        print 'ERROR: sys.argv should be of length 3'
        print 'sys.argv: %s' % (sys.argv)
        sys.exit(0)
        
    # Check to make sure that the file's name is of the correct type
    if (inputFile[-4:] != '.svg'):
        print 'ERROR: inputFile should end with .svg'
        print 'inputFile: %s' % (inputFile)
        sys.exit(0)
    
    # Check to make sure export type exists in allowable types
    if not (exportType in acceptedTypes):
        print 'ERROR export type needs to be either "png" or "eps" or "svg" or "all"'
        print 'exportType: %s' % (exportType)
        sys.exit(0)
        
    # Check to make sure svg file exists; exit if it does not
    if not os.path.exists(inputFile):
        print "ERROR: svg file doesn't exist!"
        sys.exit(0)
    
    # Split the path of the svg into a filename and a path
    path, fileName = os.path.split(inputFile)
    
    # Switch to the directory containing the svg file
    if path != '':
        os.chdir(path)
    
    file = open(fileName, "r")
    
    # parse the copied .svg file
    # I'm not sure we couldn't parse the file directly (using data = somefunc('file')) but this is what worked first
    string = file.read()
    data = etree.XML(string)
    
    #Call getImg to return a tuple of image names, and elements 
    exportList = getImgs(data)
    
    #Export all the elements of the list
    batchExport(exportType, fileName, exportList)

    
