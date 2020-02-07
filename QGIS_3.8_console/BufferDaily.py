# -*- coding: utf-8 -*-

"""
***************************************************************************
    BufferDaily.py
    ---------------------
    Date                 : February 2020
    Copyright            : (C) 2020 by César Arquero Cabral
    Email                : cesarkero@gmail.com
***************************************************************************
*                                                                         *
*   This script answers (somehow) the question from GIS_stackexchange:    *
*   "Running and scheduling processing jobs in QGIS 3"                    *
*   Reads layer and buffer it each day.                                   *
*                                                                         *
***************************************************************************
"""
__author__ = 'César Arquero Cabral'
__date__ = 'February 2020'
__copyright__ = '(C) 2020, César Arquero'

import qgis, qgis.core, glob, time, sys, threading, os
from datetime import date, timedelta, datetime
from PyQt5 import Qt
import time, threading

from qgis.core import *
from qgis.gui import *
from qgis.utils import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

#-----------------------------------------------------------------------
# parameters as objects for processing
layer = '/home/cesarkero/GoogleDrive/StackExchange/gis_stackexchange/20200109_Running and scheduling processing jobs in QGIS/input/layer.gpkg' 
t0 = '20200207_105300'
t1 = '20200207_105400'
s = 10
bufferdist = 50
bufferdiss = True
outdir = '/home/cesarkero/GoogleDrive/StackExchange/gis_stackexchange/20200109_Running and scheduling processing jobs in QGIS/output'

#-----------------------------------------------------------------------
# functions
def gpkg4QGIS (outputdir, layername):
    '''This function gets a path and a layer name and creates an string that works as gpkg output in QGIS
    processing'''
    pn = os.path.realpath(outputdir + '/' + layername + '.gpkg')
    p = f"'{pn}'"
    f = f'"{layername}"'
    return (f'ogr:dbname={p} table={f} (geom) sql=')

#-----------------------------------------------------------------------
# settings for schedule
t0 = datetime.strptime(t0, '%Y%m%d_%H%M%S')
t1 = datetime.strptime(t1, '%Y%m%d_%H%M%S')
f = timedelta(seconds=s)
ct = datetime.now()

#-----------------------------------------------------------------------------------------------------
# PROCESS
if datetime.now() > t1:
    print ("Cancel all for bad schedule")
    x.cancel()
    y.cancel()

# elif vlayer.isValid():
#     print("Layer failed to load!")

else:
    x = None

    def wait4t0():
        global x
        global t0

        x = threading.Timer(s, wait4t0)
        x.start()
        print('todavía no es la hora de empezar')

        while datetime.now() > t0:
            x.cancel()

    wait4t0()

    y = None

    def work2t1():
        global y
        global t0

        y = threading.Timer(s, work2t1)
        y.start()

        if datetime.now() > t1:
            y.cancel()

        if datetime.now() > t0:
            # Process

            # 1 set filename
            fname = str(t0)
            for i in ['-',':']:
                fname = fname.replace(i, '')
            fname.replace(" ","_")

            # 2 buffer
            print("Process time - filename:" + str(datetime.now()) + ' - ' + fname)
            inputlayer = os.path.abspath(layer)

            outputlayer = gpkg4QGIS(outdir,fname)

            print(layer)
            print(outputlayer)
            processing.run("native:buffer", {
                'INPUT': layer,
                'DISTANCE': bufferdist, 'SEGMENTS': 20, 'END_CAP_STYLE': 0, 'JOIN_STYLE': 0, 'MITER_LIMIT': 2,
                'DISSOLVE': bufferdiss,
                'OUTPUT': outputlayer})

            # update t0
            t0 = t0+f

        while t0 > t1:
            print("Processing stopped at:" + str(datetime.now()))
            y.cancel()

    work2t1()
#-----------------------------------------------------------------------------------------------------
# Tools to stop process before t1
# x.cancel()
# y.cancel()