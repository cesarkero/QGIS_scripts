##Iteradores=group
##Pyramids=name
##SelectDir=Folder

import glob, os, processing
os.chdir(SelectDir)

for layers in glob.glob( "*.tif" ):
    processing.runalg("gdalogr:overviews",
    layers,
    "2 4 8 16 32 64",
    False,0,1)