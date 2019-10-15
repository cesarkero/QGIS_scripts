##Iteradores=group
##DEMHillshade=name
##SelectDir=Folder
##SaveDir=Folder
##AzimutLuz=Number 315.000
##AltitudLuz=Number 45.000

import glob, os, processing
os.chdir(SelectDir)

for layers in glob.glob( "*.img" ):
    filename=os.path.splitext(layers)[0]
    filepath=str(SaveDir+"/"+filename+".tif")
    processing.runalg("gdalogr:hillshade",
    layers,
    1,
    False,
    False,
    1,
    1,
    AzimutLuz,
    AltitudLuz,
    filepath)