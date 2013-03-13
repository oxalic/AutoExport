Intro:
======
This is a small script that I wrote that allows for the exporting groups of 
an inkscape svg file as .png, .eps and plain svg in one simple step.

My Use Case:
===========
I use it because I am writing a paper in [pandoc](http://johnmacfarlane.net/pandoc/) and 
use a preprocessor (gpp) to automatically insert the correct format of image based 
on the target (via a simple makefile). Since I am targeting html (.svg), odf (.png) and latex/pdf(.eps), 
I want to use the best image format for each target, and unfortunately each of these 
have a different ideal image format.

Furthermore since I am writing a chemistry paper, I want images of individual compounds
as well as reactions. This allows any group to become a target for export
whether or not it is contained within a larger group also targeted for export 
and ensures that all images are updated when the master file is updated.

Instructions:
============
Make an .svg file containing all the images that your heart desires. 

Any group that you want to export simply has to have an id that begins
with any of the "prefixes" ('img:', or 'cmp:' in my case), and ends
with the name of the file that you would like to make.

Simply right click on a group and select "Object Properties" and change the
id field to <prefix>:<filename> (e.g. "img:suzukimiso"), and hit enter 
or click "set". This group will now be exported as "suzukimiso.png" 
"suzukimiso.eps" and "suzukimiso.svg".

*Protip*
:    Leave the "Object Properties" window open as you click through and 
rename all of your groups to the proper format. 

Now just call this program:

    python AutoExport.py <path to .svg file> <all | eps | png | svg>
    
and wait for it to export all the correctly named groups as seperate 
images in all selected formats.

Disclaimer etc.:
==============
I'm not very good at python, and don't really know my way around the
.svg specification or xpath or anything like that so use at your own 
risk, and feel free to let me know if there is a better way of doing 
any of this. There also are probably issues with unicode symbols or 
something like that so be careful.

Also svg export is fairly slow since it has to open and close
inkscape for every .svg image exported (because using the -z flag 
dissables using verbs), which is **very** annoying, and makes using 
your computer while this is running kind of obnoxious. 
If anyone knows a better way to set the canvas size, that would be 
amazing (perhaps it could be done with querying but I just haven't 
played around with this as I've wasted enough time getting this far). 

This code should be considered public domain.

How It Works:
=============

The meat of it is in the getImgs() function which simply uses xpath
to get all of the elements of type "group". It then iterates over 
these elements looking for id names which meet the prefix convention.
It returns a list of tuples of id names and element objects, which 
can be passed to "batchExport" along with a type and a filename. Batch
export then dispatches calls to "export" which takes an individual tuple
and either calls the inkscape to export that id (for eps and png), 
or calls svgExport which uses the etree (from lxml) to get a textual
representation of that group and then wraps that in a standard plain svg
header, and a </svg> tag footer, and writes it to a file. Then it has 
to call inkscape (and pop-open an annoying window) in order to shrink 
the canvas to fit the drawing, save the file and exit.

I have included one of the files that I use it on, feel free to test it 
with that.
