# coding: utf-8

#--------------------------
#        Imports
#--------------------------
import geopandas as gpd
from shapely.geometry import Point
import csv
import Utils
import os

"""Disclaimer
This software is preliminary or provisional and is subject to revision. It is being provided to meet the need for timely best science. The software has not received final approval by the National Institute for Space Research (INPE). No warranty, expressed or implied, is made by the INPE or the Brazil Government as to the functionality of the software and related material nor shall the fact of release constitute any such warranty. The software is provided on the condition that neither the INPE nor the Brazil Government shall be held liable for any damages resulting from the authorized or unauthorized use of the software.

Licence
MIT License
Copyright (c) 2019 Rodrigues et al.
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."""

def pontoMedio(borda,centroid):
    x = []
    y = []
    x.append(float(borda.x))
    x.append(float(centroid.x))
    y.append(float(borda.y))
    y.append(float(centroid.y))

    distancia = lambda x,y:float(((x[1]-x[0])**2)+((y[1]-y[0])**2))**0.5
    xm = lambda x:(x[0]+x[1])/2
    ym = lambda y:(y[0]+y[1])/2
    #pm = Point(xm(x),ym(y))
    return xm(x),ym(y)


sourcefile = './shp/LC8_pivots_merged_polygons.shp'
if os.path.exists(sourcefile):
    # Read circles identified using Circle Hough Transform (CHT):
    gdf = gpd.read_file('./shp/LC8_pivots_merged_polygons.shp')
else:
    print('The source file needed for this task does not exist!\nPlease, read for instructions in file -> AboutPivots_shapesMerged.txt')
    raise SystemExit

collection_points = []
for i, poly in enumerate(gdf.geometry):    
    print('Computing polygon: ',i)

    min_x, min_y, max_x, max_y = poly.bounds
    x_c,y_c = [poly.centroid.x,poly.centroid.y]

    #Define cardinal points of polygon:
    points =   [Point(x_c,max_y)]
    points.append(Point(max_x,y_c))
    points.append(Point(x_c,min_y))
    points.append(Point(min_x,y_c))

    for point in points:
        x_mean,y_mean = pontoMedio(point,poly.centroid)
        collection_points.append([i,x_mean,y_mean])

destino = './csv'
Utils.mkdir_p(destino)

# Save middlepoints in main cardinal directions of circles:
with open(destino+'/LC8_pivots_middlepoints_coords.csv', 'w') as myfile:
     wr = csv.writer(myfile, quoting=csv.QUOTE_NONE, quotechar='')
     wr.writerow(["ObjectID", "Lon", "Lat"])
     wr.writerows(collection_points)
