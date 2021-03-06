Center Pivot MATOPIBA
========================

This project contains application source code for the identification of circles of center pivots systems in remote sensing images, using Hough Transform and Time Series of Vegetation Indices. Basically, the repository has the main program (DetectingCenterPivot.py) to detected circles based on images of greenest pixels and auxiliaries programs (geoPoint.py, wtss.r and eda.py) to extract coordinates, time series of vegetation indices, and identification of center pivots according to vegetation behavior of these areas in MATOPIBA region.

Release Notes
-------------

- Support files with single band (Greenest Pixel) from LANDSAT 8

Installation
------------

**Dependencies**

    Python 2.7.X, Numpy, OpenCV, GDAL, Geopandas and Shapely
    

Build Steps
-----------

.. warning:: Build steps tested only on Ubuntu 18.04

**Setup Conda Environment**

With Conda installed [#]_, run::

  $ git clone  https://github.com/marcosmlr/CenterPivotMatopiba.git
  $ cd CenterPivotMatopiba
  $ make install
  $ conda activate CenterPivotMatopiba

.. [#] If you are using a git server inside a private network and are using a self-signed certificate or a certificate over an IP address, you may also simply use the git global config to disable the ssl checks::

  git config --global http.sslverify "false"
  
**Alternative online version of project:**

.. raw:: html

    <a href="https://colab.research.google.com/drive/1ibo9okmIPQ0HBPowLnuFB_9bFXb3B3MU?usp=sharing"><p align="center"><img src="https://colab.research.google.com/assets/colab-badge.svg"></p></a>

Usage
-----  

First of all, we need to do download the dataset (3 partial ZIP files) [#]_ containing Geotiff images of maximum response of vegetation (Greenest Pixel) measured using NDVI index in the MATOPIBA region. After download the files please use the next lines to unsplit and unzip images::

  $ zip -s 0 landsat_ndvi.zip --out landsat_ndvi_unsplit.zip
  $ unzip landsat_ndvi_unsplit.zip

.. [#] The dataset is available on Figshare collection items (https://doi.org/10.6084/m9.figshare.c.4846911) related to the paper "DETECTING CENTER PIVOTS IN MATOPIBA USING HOUGH TRANSFORM AND WEB TIME SERIES SERVICE".  


Steps to identify center pivots using Python environment:

- DetectingCenterPivot.py - program to read remote sensing images and apply Hough Transform to identify candidate circles of pivots and export these objects to shapefiles. The main function receives the wildcard name of input files. Ex. "GreenestSR_pixel_composite_2017_*.tif".

- mergeShapes.py - program to merge all shapefiles of candidate circles of pivots.
       
**Obs.:** Alternatively, we can run a command of GDAL toolkit tools to merge all shapefiles. Please see the file AboutPivots_shapesMerged.txt to further information.  

- geoPoint.py - program to read all circles identified throw Hough Transform and extract cardinals points in the middle of each circle. These points will be used for the next step, when will create Time Series of Vegetation Indices, in these points to characterize vegetation response of circles identified.  
 

Now, we need to activate R environment. Please run::  

  $ conda activate r_wtss

- wtss.r - program to read coordinates of points extracted from circles and create vegetation time series of NDVI/EVI using the API from Web Time Series Service (WTSS) of e-sensing project. 

Finally, go to the back (Python environment)::

  $ conda deactivate

- eda.py - program to analyze and filter circles detected using Hough Transform comparing vegetation behavior of these targets against Center Pivot Systems mapped from Brazilian National Water Agency (ANA) to validate results.
        
The final product of the processing is a shapefile with all center pivots identified according to thresholds of NDVI/EVI extracted from ANA pivots mapped.  


Data Processing Requirements
----------------------------

This version of the application requires the input files to be in the GeoTIFF format, compressed or not with zip or gzip.


Disclaimer
----------

This software is preliminary or provisional and is subject to revision. It is being provided to meet the need for timely best science. The software has not received final approval from the National Institute for Space Research (INPE). No warranty, expressed or implied, is made by the INPE or the Brazil Government as to the functionality of the software and related material nor shall the fact of release constitute any such warranty. The software is provided on the condition that neither the INPE nor the Brazil Government shall be held liable for any damages resulting from the authorized or unauthorized use of the software.


License
-------

MIT License

Copyright (c) 2019 Rodrigues et al.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


Authors
-------

`Rodrigues et al., (2019) <marcos.rodrigues@inpe.br>`_
