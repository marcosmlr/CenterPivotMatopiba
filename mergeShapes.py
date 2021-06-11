#Based on https://gis.stackexchange.com/a/372556
from osgeo import ogr
import os

directory = "./shp/"
outputMergefn = os.path.join(directory,'LC8_pivots_merged_polygons.shp')
outputFinalfn = os.path.join('LC8_pivots_final_results.shp')
file_start = 'LC8_pivots_'
file_ext = '.shp'
drvrname = 'ESRI Shapefile'
geomtype = ogr.wkbMultiPolygon
outputdriver = ogr.GetDriverByName('ESRI Shapefile')
    
if os.path.exists(outputMergefn):
    outputdriver.DeleteDataSource(outputMergefn)

filelist = os.listdir(directory)
if outputFinalfn in filelist:
  filelist.remove(outputFinalfn)
 
out_ds = outputdriver.CreateDataSource(outputMergefn) 
out_layer = out_ds.CreateLayer(outputMergefn, geom_type = geomtype)
    
for file in filelist:
    if file.startswith(file_start) and file.endswith(file_ext):
         print("Processing: " + file)
         ds = ogr.Open(directory + file)
         if ds is None:
             print("ds is empty")
         lyr = ds.GetLayer()
         for feat in lyr:
             out_feat = ogr.Feature(out_layer.GetLayerDefn())
             out_feat.SetGeometry(feat.GetGeometryRef().Clone())
             out_layer.CreateFeature(out_feat)
             out_layer.SyncToDisk()
