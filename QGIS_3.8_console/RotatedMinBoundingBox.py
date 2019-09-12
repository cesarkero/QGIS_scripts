from PyQt5.QtCore import *
from qgis.core import *
from qgis.gui import *
from processing.tools import *
from qgis.utils import iface
import qgis.utils, os, glob, processing, string, time, shutil, ogr

#PARAMETERS AND LAYERS
rotation = 45 #use any value between 0 and <90 #90 would make a mess

layer1 = iface.activeLayer() # Load the layer (from active)
crs = layer1.crs().authid() #get crs

#----------------------------------------------------------------------------------------
#LINE EQUATIONS
''' 
BASIC LINE EQUATIONS
y = ax + b
a = (y2 - y1) / (x2 - x1)
b = y1 - a * x1
Distance = (| a*x1 + b*y1 + c |) / (sqrt( a*a + b*b))# Function to find straight distance betweeen line and point 
'''
# slope from angle
def sfa (a):
    return round(math.tan(math.radians(a)),12) #round to avoid problems with horizontal and vertical
    
# angle from slope (not used)
def afs (s):
    return (math.atan(s) / math.pi) * 180
    
# Function to find distance 
def shortest_distance(x1, y1, a, b, c):    
    d = round(abs((a * x1 + b * y1 + c)) / (math.sqrt(a * a + b * b)) , 12)
    return d

# Function to find interception between lines
def cross(a1,b1,a2,b2):
    x = (b2-b1) / (a1-a2)
    y = a1 * x + b1
    return (x,y)

#----------------------------------------------------------------------------------------
# GET LIST OF POINTS TO ITERATE
# Calculate convexhull to reduce the iterations between point
# This avoid calculations on 'internal' points
# process of minimum bounding geometry convexHull
MBG = processing.run("qgis:minimumboundinggeometry", {'INPUT': layer1,'FIELD':None,'TYPE':3,'OUTPUT':'TEMPORARY_OUTPUT'})

# Get vertex of MBG
MBGp = processing.run("native:extractvertices", {'INPUT':MBG['OUTPUT'],'OUTPUT':'TEMPORARY_OUTPUT'})

plist = list(MBGp['OUTPUT'].getFeatures())

lp = list()
for p in plist:
    geom = p.geometry()
    a = geom.asPoint()
    point = (a[0],a[1])
    lp.append(point)

#----------------------------------------------------------------------------------------
# PROCESS
# compare hdist and v dist betweeen each pair of point and get the most distant lines
hdist_max = 0
vdist_max = 0
index = list(range(0,len(lp))) #iteration index
bl = ['ah1','bh1','av1','bv1','ah2','bh2','av2','bv2'] #polygon lines defined by 8 parameters see below

for i in index[:-1]:
    print('i'+str(i))
    for t in index[i+1:]:
        print('t'+str(t))
        
        x1 = lp[i][0] #; print('x1: {}', x1)
        y1 = lp[i][1] #; print('y1: {}', y1)
        x2 = lp[t][0] #; print('x2: {}', x2)
        y2 = lp[t][1] #; print('y2: {}', y2)
        
        #h1 equation
        ah1 = sfa(rotation)
        bh1 = y1 - ah1 * x1
        
        #v1 equation
        av1 = sfa(rotation + 90) #remember that just the horizontal is the reference at 0 rotation
        bv1 = y1 - av1 * x1 

        #h2 equation
        ah2 = sfa(rotation)
        bh2 = y2 - ah2 * x2

        #v2 equation
        av2 = sfa(rotation + 90) #remember that just the horizontal is the reference
        bv2 = y2 - av2 * x2 

        # H dist
        hdist = shortest_distance(x1, y1, ah2, -1, bh2)
        vdist = shortest_distance(x1, y1, av2, -1, bv2)
        
        if hdist > hdist_max:
            bl[0] = ah1
            bl[1] = bh1
            bl[4] = ah2
            bl[5] = bh2
            hdist_max = hdist #update max hdist
        if vdist > vdist_max:
            bl[2] = av1
            bl[3] = bv1
            bl[6] = av2
            bl[7] = bv2
            vdist_max = vdist #update max vdist

print("Max perpendicular distance betweeen 'horizontal lines' is",hdist_max, ' m')
print("Max perpendicular distance betweeen 'verticallines' is",vdist_max, ' m')

#------------------------------------------------------------------------------------------
# GET 4 COORDS FROM BOUNDINGLINES bl
# using the slope and intercept from boundinglines can we now calculate the 4 corners of the rotated polygon
H1V1 = cross(bl[0],bl[1],bl[2],bl[3]) # H1V1
H1V2 = cross(bl[0],bl[1],bl[6],bl[7]) # H1V2
H2V1 = cross(bl[4],bl[5],bl[2],bl[3]) # H2V1
H2V2 = cross(bl[4],bl[5],bl[6],bl[7]) # H2V2

# SORT POINTS CLOCKWISE AND CREATE QgsPointXY for polygon
clist = [H1V1,H1V2,H2V1,H2V2]
points=[]
points.append(sorted(clist, key=lambda e: (e[1], e[0]))[0]); clist.remove(points[0]) #minX and minY
points.append(sorted(clist, key=lambda e: (e[0], e[1]))[0]); clist.remove(points[1]) #minY and minX
points.append(sorted(clist, key=lambda e: (e[1]), reverse=True)[0]); clist.remove(points[2]) #maxY
points.append(clist[0]) #remaining
p=[]
for i in points:
    p.append(QgsPointXY(i[0],i[1]))
print('Coords of the polygon: ',p)

#------------------------------------------------------------------------------------------
#CREATE ROTATED BOUNDING BOX FROM THESE POINTS
layer = QgsVectorLayer(str('Polygon?crs='+crs), 'polygon' , 'memory')
prov = layer.dataProvider()
feat = QgsFeature()
feat.setGeometry(QgsGeometry.fromPolygonXY([p]))
prov.addFeatures([feat])
layer.updateExtents()
QgsProject.instance().addMapLayers([layer])
