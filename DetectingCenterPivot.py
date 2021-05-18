# coding: utf-8

#--------------------------
#        Imports
#--------------------------

from osgeo import osr, gdal, ogr, gdal_array
from gdalconst import *             
gdal.UseExceptions()                
from zipfile import ZipFile, is_zipfile
import numpy as np
import cv2
from timeit import default_timer as timer
import Utils
import subprocess, os, sys
import glob
import re

"""Data Processing Requirements
This version of the application requires the input files to be in the GeoTIFF format, compressed or not with zip or gzip.

Disclaimer
This software is preliminary or provisional and is subject to revision. It is being provided to meet the need for timely best science. The software has not received final approval by the National Institute for Space Research (INPE). No warranty, expressed or implied, is made by the INPE or the Brazil Government as to the functionality of the software and related material nor shall the fact of release constitute any such warranty. The software is provided on the condition that neither the INPE nor the Brazil Government shall be held liable for any damages resulting from the authorized or unauthorized use of the software.

License
MIT License
Copyright (c) 2019 Rodrigues et al.
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."""


# Notes - numpy.seterr
#
# The floating-point exceptions are defined in the IEEE 754 standard [1]:
#
#     Division by zero: infinite result obtained from finite numbers.
#     Overflow: result too large to be expressed.
#     Underflow: result so close to zero that some precision was lost.
#     Invalid operation: result is not an expressible number, typically indicates that a NaN was produced.
#
# [1]	http://en.wikipedia.org/wiki/IEEE_754
#
np.seterr(under='ignore')


#--------------------------
#        Functions
#--------------------------
# Source: https://github.com/gqueiroz/ser347/blob/master/2018/aula-18/gdal_1.ipynb
def get_band_array(filename, band_num=1, info=False):

    global dataset
    if is_zipfile(filename):
        with ZipFile(filename) as theZip:
            fileNames = theZip.namelist()
            for fileName in fileNames:
                if fileName.endswith('.tif'):
                    print("Trying open the file " + fileName)

                    try:
                        start = timer()
                        dataset = gdal.Open('/vsizip/%s/%s' % (filename, fileName))
                        end = timer()
                        print("File unziped in: ", end - start, " seconds.")

                    except:
                        del (dataset)
                        print("Opening file error!")
    else:
        print("Trying open the file " + filename)

        try:
            dataset = gdal.Open(filename)
        except:
            del(dataset)
            print("Opening file error!")

    geotransform = dataset.GetGeoTransform()
    print(geotransform)
    
    lrx = geotransform[0] + (dataset.RasterXSize * geotransform[1])
    lry = geotransform[3] + (dataset.RasterYSize * geotransform[5])

    corners = [geotransform[0], lry, lrx, geotransform[3]]
    print("The extent should be inside: " + str(corners))


    center_pivot = 500.  # tipycally radii meters
    global min_dist_px
    global min_radii_px
    global max_radii_px


    # Setup the source projection
    spatial_reference = osr.SpatialReference()
    spatial_reference.ImportFromWkt(dataset.GetProjectionRef())
   
    center_lat = np.mean([lry, geotransform[3]])
    
    if spatial_reference.GetAttrValue('unit') == 'degree': #https://gis.stackexchange.com/a/60372
        #https://stackoverflow.com/a/23875713
        #Latitude:  1 deg = 110.54 km = 110540 m
        #Longitude: 1 deg = 111.320*cos(latitude) km = 111320 * cos(latitude) m
        geotransform = list(geotransform)

        geotransform[5] =  geotransform[5] * 110540.0
        geotransform[1] = geotransform[1] * (111320.0 * np.cos(np.deg2rad(center_lat)))

    #Optimal tunned:
    min_dist_px = (center_pivot + 300.) / geotransform[1]
    min_radii_px = (center_pivot - 200.) / geotransform[1]
    max_radii_px = (center_pivot + 300.) / geotransform[1]
    print('min_dist:',min_dist_px)
    print('min_radii:',min_radii_px)
    print('max_radii_px:',max_radii_px)

    global res_x
    global res_y
    res_x = geotransform[1]
    res_y = -geotransform[5]

    if info:
        # [0] is the x coordinate of the upper left cell in raster
        # [1] is the width of the elements in the raster
        # [2] is the element rotation in x, is set to 0 if a north up raster
        # [3] is the y coordinate of the upper left cell in raster
        # [4] is the element rotation in y, is set to 0 if a north up raster
        # [5] is the height of the elements in the raster (negative)

        latitude = geotransform[3]
        longitude = geotransform[0]
        resolucao_x = geotransform[1]
        resolucao_y = -geotransform[5]

        print("Latitude inicial do dataset:", latitude)
        print("Longitude inicial do dataset:", longitude)
        print("Resolução (x) do dataset:", resolucao_x)
        print("Resolução (y) do dataset:", resolucao_y)
        print("Numero de linhas:", dataset.RasterYSize)
        print("Numero de colunas:", dataset.RasterXSize)

        # quantidade de bandas
        bandas = dataset.RasterCount

        print("Número de bandas:", bandas)

    # no caso da imagem RapidEye, as bandas 5
    # e 3 correspondem às bandas NIR e RED
    banda = dataset.GetRasterBand(band_num)


    if info:
        print("Tipos de dados:")
        print(" - banda :", gdal.GetDataTypeName(banda.DataType))

        (menor_valor, maior_valor) = banda.ComputeRasterMinMax()
        print("Menor valor:", menor_valor)
        print("Maior valor:", maior_valor)
        print("NO DATA VALUE:", banda.GetNoDataValue())

    # obtencao dos arrays numpy das bandas
    array = banda.ReadAsArray()
    print(array.min(), array.max())

    array = np.ma.masked_array(array, np.isnan(array))      

    # Exclude the pixels with no data value and normalize data
    NoData = banda.GetNoDataValue()
    print('NoData:',NoData)
    if NoData == None:
        NoData = array.min()


    print('Data type:',gdal.GetDataTypeName(banda.DataType))
    if gdal.GetDataTypeName(banda.DataType) == 'Byte':
        scale = 255.
    elif gdal.GetDataTypeName(banda.DataType) == 'Int16':
        scale = 10000.
    elif gdal.GetDataTypeName(banda.DataType) == 'UInt16':
        scale = 65535. #Landsat8
    elif gdal.GetDataTypeName(banda.DataType) == 'Float64':
        scale = 1.  # Nothing to do
    elif gdal.GetDataTypeName(banda.DataType) == 'Float32':
        scale = 1.  # Nothing to do NDVI Greenest pixel from Earth Engine   
    else:
        raise TypeError("band type:",gdal.GetDataTypeName(banda.DataType),"not allowed!")
    
    if np.isnan(array).any():
        marray = np.ma.masked_invalid(array) #Mask NAN and Inf
    else:
        marray = np.ma.masked_where(array == NoData, array / scale) #When condition tests floating point values for equality, consider using masked_values instead.
        print('antes invalid:',marray.min(), marray.max())
    
    if gdal.GetDataTypeName(banda.DataType) != 'Float64' and\
       gdal.GetDataTypeName(banda.DataType) != 'Float32':
        marray = np.ma.clip(marray, 0.0, 1.0)

    return marray

    # close the dataset and clean the memory
    dataset = None



def export_circles_detected(circles, filename_out, type='shp', targetEPSG=4326):
    if circles is not None:
        if circles.dtype == 'float32':
            # convert the (x, y) coordinates and radius of the circles to integers
            circles = np.round(circles[0, :]).astype("int")

        geotransform = dataset.GetGeoTransform()

        circles_features = []
        # loop over the (x, y) coordinates and radius of the circles
        for x, y, r in circles:
            lrx = geotransform[0] + (x * geotransform[1])
            lry = geotransform[3] + (y * geotransform[5])

            #print('Index (x,y):',x,y)
            #print('Coordinators(lon,lat):',lrx,lry)
            circles_features.append([lrx,lry,r * geotransform[1]])

        geoCollection = Utils.create_geoCollection(circles_features)

        spatial_reference = osr.SpatialReference()
        spatial_reference.ImportFromWkt(dataset.GetProjectionRef())
        target = spatial_reference

        if spatial_reference.GetAttrValue("AUTHORITY", 1) != targetEPSG:
            print('Origem:\n', spatial_reference)

            target = osr.SpatialReference()
            target.ImportFromEPSG(targetEPSG)
            print('Destino:\n', target)

            transform = osr.CoordinateTransformation(spatial_reference, target)
            geoCollection.Transform(transform)


        if type == 'shp':
            destino = './shp'
            Utils.mkdir_p(destino)

            Utils.write_shapefile(geoCollection,
                                  target,
                                  ogr.wkbPolygon,
                                  os.path.join(destino,filename_out+'_polygon.shp'))
        elif type == 'geojson':
            destino = './geojson'
            Utils.mkdir_p(destino)

            Utils.write_geojson(geoCollection,
                                target,
                                ogr.wkbGeometryCollection,
                                os.path.join(destino, filename_out+'.geojson'))

    else:
        print('None circles detected!')


# https://www.pyimagesearch.com/2015/04/06/zero-parameter-automatic-canny-edge-detection-with-python-and-opencv/
def auto_canny(image, sigma=0.33):
    # compute the median of the single channel pixel intensities
    v = np.ma.median(image)

    # apply automatic Canny edge detection using the computed median
    lower = int(max(0, (1.0 - sigma) * v))
    upper = int(min(255, (1.0 + sigma) * v))

    start = timer()
    edged = cv2.Canny(image, lower, upper)
    end = timer()
    print("Edged in: ", end - start," seconds.")
    print('median:', v, 'lower:', lower, ' upper:', upper)

    # return the edged image
    return edged


def finding_circles(auto, dp_value=1, min_dist_px=40,
                    param1=50,param2=15,
                    min_radii_px=15, max_radii_px=40):
    #######################################################
    # Hough Transform to detect Lines and Circles:
    ######################################
    """method = cv2.HOUGH_GRADIENT based on 2-1 Hough Transform (2HT)
       Reference: YUEN, H.; PRINCEN, J.; ILLINGWORTH, J.; KITTLER, J. 
                  Comparative study of Hough Transform methods for circle 
                  finding. Image and Vision Computing, v. 8, n. 1, p. 71–77, fev. 1990."""

    """Center pivots are typically less than 1600 feet (500 meters) in length (circle radius)
    with the most common size being the standard 1/4 mile (400 m) machine. A typical 1/4 mile
    radius crop circle covers about 125 acres of land"""

    # minRadius: Minimum size of the radius (in pixels).
    # maxRadius: Maximum size of the radius (in pixels).
    print('Parameters for HoughCircles: dp:', dp_value,'minDist:', min_dist_px,
          'param1:',param1,'param2:',param2,'minRadius:', min_radii_px,
          'maxRadius:',max_radii_px)

    # detect circles in the image
    circles = cv2.HoughCircles(auto, cv2.HOUGH_GRADIENT,
                               dp=dp_value, minDist=min_dist_px,
                               param1=param1, param2=param2,
                               minRadius=int(min_radii_px), maxRadius=int(max_radii_px))


    # ensure at least some circles were found
    if circles is not None:
        # Remove circles with radii missing value:
        circles_tmp = np.delete(circles, np.where(circles[:, :, 2] == 0.), axis=1)

        if circles_tmp.size == 0:
            circles = None
        else:
            circles = circles_tmp
            print('Nr. Circles Detected:', circles.shape[1])

    return circles



###############################################
# MAIN PROGRAM
################################################
imgs_folder = "./landsat_ndvi"
sat_name = "LC8_"

def main(inputfile):
    for file in glob.glob(os.path.join(imgs_folder,inputfile)):
        path = os.path.basename(file).split('_')[4][0:3]
        row = os.path.basename(file).split('_')[4][3:5]
                        
        """Satellite maps of vegetation show the density of plant growth over the entire 
        globe. The most common measurement is called the Normalized Difference Vegetation
         Index (NDVI). Very low values of NDVI (0.1 and below) correspond to barren areas 
         of rock, sand, or snow. Moderate values represent shrub and grassland (0.2 to 0.3), 
         while high values indicate temperate and tropical rainforests (0.6 to 0.8).
         https://earthobservatory.nasa.gov/Features/MeasuringVegetation"""

        #####################################################################
        # Normalizaded Difference Vegetation Index (Rouse et al.,1973):
        array_ndvi = get_band_array(file, info=False).astype('float')
        print("NDVI limits:", array_ndvi.min(), array_ndvi.max())        
        
        array_ndvi = np.ma.array(array_ndvi, mask=np.isnan(array_ndvi))  # Use a mask to mark the NaNs
        array = np.uint8(Utils.norm_minmax(array_ndvi, 0, 255)) #para Canny OpenCV
        array_mask = np.ma.getmask(array_ndvi)

        # Apply Canny:
        edges = auto_canny(array, sigma=0.33)
          
        
        # Threshold for Bare soil (SANTOS et al.,2018)
        # DOI: https://doi.org/10.15809/irriga.2015v1n2p30
        with np.errstate(invalid='ignore'):
            edges[(array_ndvi <= 0.56)] = 0
        
        edges[array_mask] = 0 #remove edges pixels marked as NaNs in NDVI array                    
        
        min_dist_px = 34;  min_radii_px= 10.0; max_radii_px= 34 
        dp_value=1; par1=50; par2=15
        circles = finding_circles(edges,dp_value=dp_value,min_dist_px=min_dist_px,
                                  param1=par1,param2=par2,
                                  min_radii_px=min_radii_px,max_radii_px=max_radii_px)
        

        """ Spatial reference for output EPSG_value = 4326 (Transformation if necessary)
            type can be 'shp' for 'geojson'"""
        
        spatial_reference = osr.SpatialReference()
        spatial_reference.ImportFromWkt(dataset.GetProjectionRef())
        EPSG_value = spatial_reference.GetAttrValue("AUTHORITY", 1)
        export_circles_detected(circles,sat_name+'pivots_'+path+row, type='shp',
                                  targetEPSG=EPSG_value)


if __name__ == "__main__":
    main('GreenestSR_pixel_composite_2017_*.tif')
