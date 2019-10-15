##Solar=group
##SunHours=name
##MDE=raster
##Output=folder
##Dias=string 79,172,266,355

from PyQt4.QtCore import QFileInfo, QSettings, QVariant
from qgis.core import *
import qgis.utils
import os, glob, processing, string, time, shutil

MDE ="Z:/Proxectos/589_astillero_4_0/5_gis/paisaje/Sombreado/MDE_cota_clip2.tif"
Output ="Z:/Proxectos/589_astillero_4_0/5_gis/paisaje/Sombreado/Insolacion"
Dias = "79,172,266,355"

#calculo de extension
rasterlayer = QgsRasterLayer(MDE,"rasterlayer")
rasterext = rasterlayer.extent()
xmin = rasterext.xMinimum()
xmax = rasterext.xMaximum()
ymin = rasterext.yMinimum()
ymax = rasterext.yMaximum()
extension = "%f,%f,%f,%f" %(xmin, xmax, ymin, ymax)

#Procesado para cada dia introducido
d = Dias.split(',')
for d in d:
	nfile = str(Output+'/'+'SunHours_'+str(d)+'.tif')
	print("Procesando :" + str(nfile))
	processing.runalg("grass7:r.sun",
	MDE,
	MDE,
	MDE,
	None,None,None,None,None,None,
	d,0.5,0,1,False,False,extension,0,None,nfile,None,None,None)