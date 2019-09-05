# -*- coding: utf-8 -*-

"""
***************************************************************************
    WaterOutletIterator.py
    ---------------------
    Date                 : September 2019
    Copyright            : (C) 2019 by César Arquero Cabral
    Email                : cesarkero@gmail.com
***************************************************************************
*                                                                         *
*   This script answers (somehow) the question from GIS_stackexchange:    *
*   "Rockfall analysis (Nearest neighbor downhill) in QGIS"               * 
*   This makes an iteration over a point layer, calculates r.water.outlet * 
*   for each point, polygonize the result and then merges all             *  
*   the polygon layers. Each wateroutlet is identified by the fid.        *  
*                                                                         *
***************************************************************************
"""
__author__ = 'César Arquero Cabral'
__date__ = 'September 2019'
__copyright__ = '(C) 2019, César Arquero'

from qgis.PyQt.QtCore import QCoreApplication, QVariant
from osgeo import gdal
from qgis.core import (QgsFields,
                       QgsField,
                       QgsFeature,
                       QgsProcessing,
                       QgsFeatureSink,
                       QgsProcessingUtils,
                       QgsVectorLayer,
                       QgsRasterLayer,
                       QgsProcessingOutputFolder,
                       QgsProcessingParameterFileDestination,
                       QgsProcessingException,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterRasterLayer,
                       QgsProcessingParameterFeatureSink,
                       QgsProcessingParameterBoolean,
                       QgsProcessingParameterField)
from qgis import processing, os
import glob

class WaterOutletIterator(QgsProcessingAlgorithm):
    
    INPUT1 = 'INPUT1'
    INPUT2 = 'INPUT2'
    FID = 'FID'
    OUTDIR = 'OUTDIR'
    KEEPTEMP = 'KEEPTEMP'
    OUTPUT = 'OUTPUT'

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterFeatureSource(
                self.INPUT1,
                self.tr('Select stop points'),
                [QgsProcessing.TypeVectorAnyGeometry]))
        self.addParameter(QgsProcessingParameterField(
                self.FID,
                'Choose id field',
                'fid',
                self.INPUT1))
        self.addParameter(QgsProcessingParameterRasterLayer(
                self.INPUT2,
                self.tr('Select flowdir raster'),
                'flowdir'))
        self.addParameter(QgsProcessingParameterFileDestination(
                self.OUTDIR,
                self.tr('Output dir'),
                defaultValue = 'D:/WaterOutletIterator/'))
        self.addParameter(QgsProcessingParameterBoolean(
                self.KEEPTEMP,
                self.tr('keep temporal files'),
                defaultValue = True))
        self.addParameter(QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                self.tr('Output')))
                
    def processAlgorithm(self, parameters, context, feedback):
        #parameters as objects for processing
        points = self.parameterAsSource(parameters, self.INPUT1, context)
        fid_field = self.parameterAsString(parameters, self.FID, context)
        flowdir = self.parameterAsRasterLayer(parameters, self.INPUT2, context)
        keeptemp = self.parameterAsBool(parameters, self.KEEPTEMP, context)
        outdir = self.parameterAsString(parameters, self.OUTDIR, context)
        
        #-----------------------------------------------------------------------
        #DEFINE SINK (OUTPUT)
        fields = points.fields() #define fields
        crs = points.sourceCrs() #defining CRS
        (sink, dest_id) = self.parameterAsSink(parameters, self.OUTPUT, context, fields, 3, crs)

        if sink is None:
            raise QgsProcessingException(self.invalidSinkError(parameters, self.OUTPUT))
              
        # Send some information to the user
        feedback.pushInfo('CRS is {}'.format(crs.authid()))

        # Compute the number of steps to display within the progress bar 
        total = 100.0 / points.featureCount() if points.featureCount() else 0
        
        #-----------------------------------------------------------------------
        #check and create temp folderimport os
        tempdir = str(outdir+"temp/")
        if not os.path.exists(tempdir):
            os.makedirs(tempdir)

        #-----------------------------------------------------------------------
        #ITERATION OVER POINTS AND PROCESS
        for current, f in enumerate(points.getFeatures()):
            #unique identifier
            fid = int(f[fid_field])
            
            # Stop the algorithm if cancel button has been clicked
            if feedback.isCanceled():
                break
            if not f.hasGeometry():
                continue
            
            # Info and Update the progress bar
            feedback.pushInfo ("Processing id: {}".format(fid))
            feedback.setProgress(int(current * total))

            #-------------------------------------------------------------------
            #r.water.outlet
            feedback.pushInfo ("r.water.outlet: {}".format(fid)) 
            outtif = str(tempdir+"wateroutlet_"+str(fid)+".tif") #name
            
            #create coordinate of point
            geom = f.geometry()
            a = geom.asPoint()
            point = str(str(int(a[0]))+','+str(int(a[1]))+'[EPSG:25833]')   
    
            rwateroutlet = processing.run("grass7:r.water.outlet",{
                    'input':flowdir,
                    'coordinates':point,
                    'output': outtif,
                    'GRASS_REGION_PARAMETER':None,
                    'GRASS_REGION_CELLSIZE_PARAMETER':0,
                    'GRASS_RASTER_FORMAT_OPT':'',
                    'GRASS_RASTER_FORMAT_META':''},
                context=context, feedback=feedback)
            
            tempras = QgsRasterLayer(outtif)
            
            #-------------------------------------------------------------------
            #polygonize
            feedback.pushInfo ("polygonize: {}".format(fid))
            outpol = str(tempdir+"polygonize_"+str(fid)+".shp") #name
            
            polygonize = processing.run("gdal:polygonize", {
                    'INPUT':tempras,
                    'BAND':1,
                    'FIELD':'x',
                    'EIGHT_CONNECTEDNESS':False,
                    'OUTPUT': outpol},
                context=context, feedback=feedback)
            
            tempshp = QgsVectorLayer(outpol, "tempshp", "ogr")
            
            # Read the polygonized layer and create output features
            for t in tempshp.getFeatures():
                t.setFields(fields) #set same fields as input
                t['fid'] = f['fid'] #update fid
                t['hoyde'] = f['hoyde'] #update hoyde???
                sink.addFeature(t, QgsFeatureSink.FastInsert)
            
            #-------------------------------------------------------------------
            #REMOVE FILES
            #check if temporal files must be removed
            if keeptemp == False: 
                #delete objects to avoid windows 32 error
                del tempshp
                del tempras
                tempfiles = glob.glob(str(tempdir+'*'))
                feedback.pushInfo("Removing: {}".format(tempfiles))
                for file in tempfiles:
                    os.remove(file)
                
        return {self.OUTPUT: dest_id}
        
#-------------------------------------------------------------------------------
    def tr(self, string):
        return QCoreApplication.translate('Processing', string)
    
    def createInstance(self):
        return WaterOutletIterator()
        
    def name(self):
        return 'WaterOutletIterator'

    def displayName(self):
        return self.tr('Water Outlet Iterator')

    def group(self):
        return self.tr('GIS_stackexchange')

    def groupId(self):
        return 'GIS_stackexchange'
        
    def shortHelpString(self):
        return self.tr("Iterates over point layer, executes r.water.outlet, polygonize and merge all layers")
