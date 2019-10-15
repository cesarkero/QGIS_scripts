##Viewshed=group
##Viewshed=name
##Puntos=vector Point
##MDE=raster
##Output=folder
##AtributoAltura=string Altura
##AltElem=number 180
##AltObs=number 1.8
##Distancia=string 5000
##Memoria=number 2000
##CurvTer=boolean TRUE
##RefAtm=boolean TRUE
##Acumulado=boolean TRUE

from PyQt4.QtCore import QFileInfo, QSettings, QVariant
from qgis.core import *
import qgis.utils
import os, glob, processing, string, time, shutil, os.path, subprocess

#crear capa vectorial a partir de la ruta anterior
layer = QgsVectorLayer(Puntos, "testlayer_shp", "ogr")
features = layer.getFeatures()

#crear lista vacia para meter los rasters que despues seran sumados
lista = list()

#extension del raster (servira para los procesos posteriores)
rasterlayer = QgsRasterLayer(MDE,"rasterlayer")
rasterext = rasterlayer.extent()
xmin = rasterext.xMinimum()
xmax = rasterext.xMaximum()
ymin = rasterext.yMinimum()
ymax = rasterext.yMaximum()
extension = "%f,%f,%f,%f" %(xmin, xmax, ymin, ymax)

#iterar sobre features de capa de puntos y ejecutar viewshed para cada punto
count=int(1)
for f in features:
	geom = f.geometry()
	# crear coordenada de punto
	a = geom.asPoint()
	punto = str(str(int(a[0]))+','+str(int(a[1])))
	id = str(count)
	# nombre de archivo de salida y lista con los archivos creados
	salida = str(Output+"/"+"viewshed"+"_"+id+".tif")
	lista.append(salida)
	
	#si el campo AtributoAltura no esta vacio pillar el valor de ese atributo de cota altura o lo que sea
	#si esta vacio entonces pillar el valor de AltElem
	if AtributoAltura !="":
		Altura = f[AtributoAltura]
	elif AtributoAltura == "":
		Altura = AltElem
	
	if os.path.isfile(salida) is not True:
		print ("Procesando id:"+' '+id)
		# proceso de viewshed
		processing.runalg('grass7:r.viewshed',
		MDE,
		punto,
		Altura,
		AltObs,
		Distancia,
		0.14286,
		Memoria,
		CurvTer,
		RefAtm,
		True,False,
		extension,
		0,
		salida)
		count+=1

#suma de rasters
if Acumulado == True:
	AcumuladoTif = str(Output+"/"+"viewshed"+"_"+"acumulado"+".tif")
	if os.path.isfile(AcumuladoTif) is not True:
		print ("Procesando raster acumulado")
		processing.runalg("grass7:r.series",lista,False,10,"-10000000000,10000000000",extension,0,AcumuladoTif)
