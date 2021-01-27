# coding: utf-8

#--------------------------
#        Imports
#--------------------------
import geopandas as gpd
import pandas as pd
import numpy as np
import Utils
import matplotlib.pyplot as plt
import gc

np.seterr(invalid='ignore') # To disable RuntimeWarning: invalid value encountered in greater, because NaN an Inf values  

"""Disclaimer
This software is preliminary or provisional and is subject to revision. It is being provided to meet the need for timely best science. The software has not received final approval by the National Institute for Space Research (INPE). No warranty, expressed or implied, is made by the INPE or the Brazil Government as to the functionality of the software and related material nor shall the fact of release constitute any such warranty. The software is provided on the condition that neither the INPE nor the Brazil Government shall be held liable for any damages resulting from the authorized or unauthorized use of the software.

Licence
MIT License
Copyright (c) 2019 Rodrigues et al.
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."""

# Read circles identified using Circle Hough Transform (CHT):
gdf = gpd.read_file('./shp/LC8_pivots_merged_polygons.shp')
print(gdf.head())

what_veg = {'EVI':True,'NDVI':True}
if what_veg['EVI']:
    veg_ind = 'EVI' #'NDVI' or 'EVI'
    # Read vegetation index time series extracted from middlepoint of main cardinal directions of center pivots:
    data_evi = pd.read_csv('./csv/LC8_pivots_middlepoints_'+veg_ind.lower()+'_TS.csv')
    data_evi['Date'] = pd.to_datetime(data_evi['Date'])
    data_evi = data_evi.set_index('Date')
    print('\n Samples of '+veg_ind)
    print(data_evi.head())

    #https://www.datacamp.com/community/tutorials/moving-averages-in-pandas
    print('\n Calculating EVI Simple Moving Average (SMA), 4 samples for each circle detected!')
    data_evi_sma = data_evi.iloc[:,:].rolling(window=4,axis=1).mean()
    print(data_evi_sma.head())
    del [[data_evi]]
    
    # Standard deviation of each time series samples
    #std_evi = np.array(data_evi.std())
    std_evi = np.array(data_evi_sma.iloc[:,3::4].std())

    # amplitude of each time series samples
    #amplitude_evi = np.array(data_evi[:].max() - data_evi[:].min())
    amplitude_evi = np.array(data_evi_sma.iloc[:,3::4].max() - data_evi_sma.iloc[:,3::4].min())

if what_veg['NDVI']:
    veg_ind = 'NDVI' #'NDVI' or 'EVI'
    # Read vegetation index time series extracted from middlepoint of main cardinal directions of center pivots:
    data_ndvi = pd.read_csv('./csv/LC8_pivots_middlepoints_'+veg_ind.lower()+'_TS.csv')
    data_ndvi['Date'] = pd.to_datetime(data_ndvi['Date'])
    data_ndvi = data_ndvi.set_index('Date')
    print('\n Samples of '+veg_ind)
    print(data_ndvi.head())

    print('\n Calculating NDVI Simple Moving Average (SMA), 4 samples for each circle detected!')
    data_ndvi_sma = data_ndvi.iloc[:,:].rolling(window=4,axis=1).mean()
    print(data_ndvi_sma.head())
    del [[data_ndvi]]

    # Standard deviation of each time series samples
    #std_ndvi = np.array(data_ndvi.std())
    std_ndvi = np.array(data_ndvi_sma.iloc[:,3::4].std())

    # amplitude of each time series samples
    #amplitude_ndvi = np.array(data_ndvi[:].max() - data_ndvi[:].min())
    amplitude_ndvi = np.array(data_ndvi_sma.iloc[:,3::4].max() - data_ndvi_sma.iloc[:,3::4].min())

# Identify missing samples:
# missing = np.argwhere(np.isnan(std))
# print(data.iloc[:,np.squeeze(missing)])

#Clean objects:
gc.collect()
del gc.garbage[:]

#indexs_threshold = np.where( (std_ndvi > 0.20) & (amplitude_ndvi > 0.56)) #835/868 pivots
#indexs_threshold = np.where( (std_ndvi > 0.05) & (amplitude_ndvi > 0.07)) #1196/1388
#indexs_threshold = np.where( (std_ndvi > 0.026) & (amplitude_ndvi > 0.07)) #1222/1422
#indexs_threshold = np.where( (std_ndvi > 0.02) & (amplitude_ndvi > 0.06)) #1224/1424

#indexs_threshold = np.where(((std_evi > 0.01) & (amplitude_ndvi > 0.05)) & ((std_ndvi > 0.02) & (amplitude_ndvi > 0.06)) ) #1224/1424
#indexs_threshold = np.where(((std_evi > 0.03) & (amplitude_ndvi > 0.07)) & ((std_ndvi > 0.02) & (amplitude_ndvi > 0.06)) ) #1224/1423
indexs_threshold = np.where(((std_evi > 0.02) & (amplitude_ndvi > 0.07)) & ((std_ndvi > 0.02) & (amplitude_ndvi > 0.06)) ) #1224/1424

#print(std_evi[indexs_threshold])
#print(amplitude_evi[indexs_threshold])

# Era necessario quanto era considerado todas as amostras, agora usa-se Moving Average a cada 4 amostras:
#print(df.loc[indexs_threshold])
#print(np.unique(df.loc[indexs_threshold].values))
#print(gdf.loc[np.unique(df.loc[indexs_threshold].values)])
#for poly in gdf.loc[np.unique(df.loc[indexs_threshold].values)].geometry:
#    #print(poly.exterior.coords.xy)
#    print(poly.centroid)
# FIM - Era necessario quanto era...


gdf_out = gdf.loc[indexs_threshold]

# Read pivots mapped from ANA:
gdf_ana = gpd.read_file('/home/image/src/python/cap240/TrabFinal/shp_ext/ANA_EMBRAPA_PivosMatopiba_Mapeados2017.shp')

##############################
# Intersects:
###############
#f = lambda x:np.sum(gdf.intersects(x))
#inter = gdf_ana['geometry'].apply(f)
#print(inter[inter>0].shape)


#https://www.e-learn.cn/topic/2597069
# generate spatial index
sindex = gdf_out.sindex
# define empty list for results
results_list = []
index_results_list = []
# iterate over the polygons
for poly in gdf_ana['geometry']:
    # find approximate matches with r-tree, then precise matches from those approximate ones
    possible_matches_index = list(sindex.intersection(poly.bounds))
    possible_matches = gdf_out.iloc[possible_matches_index]
    precise_matches = possible_matches[possible_matches.intersects(poly)]
    if len(precise_matches) > 0:
        index_results_list.append(precise_matches.index.values)
        
    results_list.append(len(precise_matches))

result_tmp =  sum(i > 0 for i in results_list)
index_pivots = np.unique(np.concatenate(index_results_list, axis=0), axis=0) #Remove duplicates
print('\nQuantity of circles of pivots detected matching with mapped by ANA '+ str(result_tmp) + ' from '+ str(index_pivots.shape[0]))


### Plot STD histogram of the data
##n, bins, patches = plt.hist(std_evi[index_pivots], bins='auto',
##                            density=False, facecolor='b', alpha=0.75)
##
##print(n,bins,patches)
##
##plt.xlabel('Standard deviation')
##plt.ylabel('Quantity')
##plt.title('EVI standard deviation of detected pivots filtered with ANA pivots')
##plt.grid(True)
##plt.savefig('EVI_std_pivots_detected_filtered_usingNDVI.png',bbox_inches='tight',dpi=150)
##
##plt.clf()
### Plot amplitude histogram of the data
##n, bins, patches = plt.hist(amplitude_evi[index_pivots], bins='auto',
##                            density=False, facecolor='g', alpha=0.75)
##
##print(n,bins,patches)
##
##plt.xlabel('Amplitude')
##plt.ylabel('Quantity')
##plt.title('EVI amplitude of detected pivots filtered with ANA pivots')
##plt.grid(True)
##plt.savefig('EVI_amplitude_pivots_detected_filtered_usingNDVI.png',bbox_inches='tight',dpi=150)

destino = './shp'
Utils.mkdir_p(destino)

# Save result after filter the  circles based on vegetation index behavior:
#gdf.loc[np.unique(df.loc[indexs_threshold].values)].to_file(destino+"/LC8_pivots_final_results.shp")
gdf.loc[index_pivots].to_file(destino+"/LC8_pivots_final_results.shp")

print('-> Final result exported to shapefile '+ destino+ "/LC8_pivots_final_results.shp")


