Center Pivot MATOPIBA
========================

This project contains application source code for the identification of candidates circles of center pivots systems in remote sensing images, using Hough Transform and Time Series of Vegetation Indices. Basically, the path has a main module (DetectingCenterPivot.py) to detected circles based on images of greenest pixels and submodules (ReSSIM and CenterPivot) to  serching specific targets how burned areas or center pivot irrigation areas in remote sensing images.

Release Notes
-------------

- Support files with single band (Greenest Pixel) from LANDSAT 8

Installation
------------

**Dependencies**

    Python 2.7.X, Numpy, OpenCV, GDAL, Geopandas and Shapely
    

Build Steps
-----------

**Setup Conda Environment** 

With Conda installed [#]_, run::

  $ git clone  https://github.com/marcosmlr/CenterPivotMatopiba.git
  $ cd CenterPivotMatopiba
  $ make install
  $ conda activate CenterPivotMatopiba

.. [#] If you are using a git server inside a private network and are using a self-signed certificate or a certificate over an IP address ; you may also simply use the git global config to disable the ssl checks::

  git config --global http.sslverify "false"


Usage
-----

First of all, we need to do download the dataset (3 partial ZIP files) [#]_ containing Geotiff images of maximum response of vegetation (Greenest Pixel) measured using NDVI index in the MATOPIBA region. Please use the next lines to unsplit and unzip images:
  $ zip -s 0 landsat_ndvi.zip --out landsat_ndvi_unsplit.zip
  $ unzip landsat_ndvi_unsplit.zip

.. [#] The dataset is available on Figshare collection items (https://figshare.com/account/home#/collections/4846911) related to the paper "DETECTING CENTER PIVOTS IN MATOPIBA USING HOUGH TRANSFORM AND WEB TIME SERIES SERVICE".

Source code modules (Steps to identify Center Pivots Systems) using Python environment:

 - DetectingCenterPivot.py - program to read remote sensing images and apply Hough Transform to identify candidate circles of pivots and export this objects to shapefiles
       The main function receive wildcard name of input files. Ex. "GreenestSR_pixel_composite_2017_*.tif". 
**Obs.:** After this process, we need to run a command of GDAL toolkit tools to merge all shapefiles. Please see file AboutPivots_shapesMerged.txt to further information.
 - geoPoint.py - program to read all circles identified throw Hough Transform and extract cardinals points in the middle of each circle. These points will be used for the next step, when will create Time Series of Vegetation Indices, in these points to characterize vegetation response of circles identified.

Now, we need activate R environment. Please run:
  conda activate r_wtss

  - wtss.r - program to read coordinates of points extracted from circles and create vegetation time series of NDVI/EVI using the API from Web Time Series Service (WTSS) of e-sensing project. 

Finally, go to back (Python environment):
  conda deactivate

  - eda.py - program to analyse and filter circles detected using Hough Transform comparing vegetation behavior of this targets against Center Pivot Systems mapped from Brazilian National Water Agency (ANA) to validate results.
        The final product of the processing is a shapefile with all center pivots identified according to threshods of NDVI/EVI extracted from ANA pivots mapped.  


Data Processing Requirements
----------------------------

This version of the application requires the input files to be in the GeoTIFF format, compressed or not with zip or gzip.


Disclaimer
----------

This software is preliminary or provisional and is subject to revision. It is being provided to meet the need for timely best science. The software has not received final approval by the National Institute for Space Research (INPE). No warranty, expressed or implied, is made by the INPE or the Brazil Government as to the functionality of the software and related material nor shall the fact of release constitute any such warranty. The software is provided on the condition that neither the INPE nor the Brazil Government shall be held liable for any damages resulting from the authorized or unauthorized use of the software.


Licence
-------

MIT License

Copyright (c) 2019 Rodrigues et al.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


Authors
-------

`Rodrigues et al. <marcos.rodrigues@inpe.br>`_.
