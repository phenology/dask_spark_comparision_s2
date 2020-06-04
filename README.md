# Dask Spark comparison

This project comparing Dask and Spark by applying them in the same test case: computing NDVI values with Sentinel-2 images.


1. Download Sentinel-2 images
You need to execute `download_s2.js` in [Google Earth Engine](https://code.earthengine.google.com/). 

Configure the time span:

```javascript
    var s2 = ee.ImageCollection('COPERNICUS/S2')
        .filterDate('2018-01-01', '2019-12-01')
```

Configure the image area:
```javascript
    var poly_test = ee.Geometry.Rectangle([4.2346171335651706,51.944589555395,4.324567695088608,51.989855970508636]);
```

The script will export the images to your Google Drive.


2. Compute NDVI with both Dask and Spark
The NDVI is computed in `spark_vs_dask.py`. In this script we compute NDVI for a single S2 image by function `ndvi`, and export the ndvi as png image. We execute the same function and the same input data through both Dask and Spark framework. We export results in `./out` directory. There will also be a plot showing the execution wall time for Spark and Dask, when excecuting different number of images and with different number of workers.

You can simply start executing the comparision by:

```bash
    python3 spark_vs_dask.py
```

You can configure the number of workers and the number of images to execute:

```bash
    list_nr_workers = [1,2,3,4]
    list_nr_img = range(5,31,5)
```

The script will run though all combinations of the two lists.
