##Solar=group
##SombrasDia=name
##MDE=raster
##Output=folder
##Fecha=string 20190320
##SunriseSunset=string 0630_2200
##CadaMin=number 30

from PyQt4.QtCore import QFileInfo, QSettings, QVariant
from qgis.core import *
import qgis.utils
import os, glob, processing, string, time, shutil

MDE ="Z:/Proxectos/589_astillero_4_0/5_gis/paisaje/Sombra/MDEviewshed_clip2.tif"
Output ="Z:/Proxectos/589_astillero_4_0/5_gis/paisaje/Sombra/Raster"
Fecha = "20190320"
SunriseSunset = "0630_2200"
CadaMin = 30

rasterlayer = QgsRasterLayer(MDE,"rasterlayer")
rasterext = rasterlayer.extent()
xmin = rasterext.xMinimum()
xmax = rasterext.xMaximum()
ymin = rasterext.yMinimum()
ymax = rasterext.yMaximum()
extension = "%f,%f,%f,%f" %(xmin, xmax, ymin, ymax)

#generar parametros para sunmask (ints a partir de los strings de entrada)
AAAA=int(Fecha[0:4])
MM=int(Fecha[4:6])
DD=int(Fecha[6:8])
HHi=int(SunriseSunset[0:2])
HHf=int(SunriseSunset[5:7])
HH=range(HHi,HHf)
mm=range(0,60,CadaMin)

for H in HH:
	for m in mm: 
		nfile = str(Output+'/'+'S_'+Fecha+'_'+str(H).zfill(2)+str(m).zfill(2)+'.tif')
		print("Procesando :" + str(nfile))
		processing.runalg("grass7:r.sunmask.datetime",MDE,AAAA,MM,DD,H,m,0,0,xmin,ymin,True,False,extension,0,nfile)