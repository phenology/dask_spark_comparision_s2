# Dask vs pySpark comparison by running the same job
# Loading Sentinel2 tiff, compute NDVI and export to png

from osgeo import gdal
from pyspark import SparkContext
from dask.distributed import Client, LocalCluster
from matplotlib import pyplot as plt
import os
import pathlib
import time
import numpy as np


def export_ndvi(in_out_file_pairs):
    # Function to compute NDVI
    # For S2 NIR=B4, VIR=B8
    s2_file = in_out_file_pairs[0]
    outfile = in_out_file_pairs[1]
    # Load image
    img = gdal.Open(s2_file)
    # Compute NDVI
    nir = np.array(img.GetRasterBand(4).ReadAsArray())
    vir = np.array(img.GetRasterBand(8).ReadAsArray())
    ndvi = (nir-vir)/(nir+vir)
    # Export tiff
    # plt.imshow(ndvi)
    # plt.savefig(outfile)
    return

if __name__ == '__main__':
    list_nr_workers = [1,2,4]
    list_nr_img = range(50,100,10)
    s2_data_dir =  pathlib.Path('./s2_images/')
    output_dir_ndvi = './out/ndvi'
    output_dir_time = './out/time'
   
    figure_time = plt.figure('time')
    for nr_worker in list_nr_workers:
        # Record time for both 
        time_dask= []
        time_spark = []
        for nr_img in list_nr_img:
            # Setting in/out path 
            out_dir_dask = output_dir_ndvi + 'dask_workers{}_IMG{}/'.format(nr_worker, nr_img)
            out_dir_spark = output_dir_ndvi + 'spark_workers{}_IMG{}/'.format(nr_worker, nr_img)
            os.makedirs(out_dir_dask) if not os.path.exists(out_dir_dask) else None
            os.makedirs(out_dir_spark) if not os.path.exists(out_dir_spark) else None
            in_out_file_pairs_dask= [(f.as_posix(), out_dir_dask + f.stem+'_NDVI.png') for f in s2_data_dir.iterdir() if f.suffix == '.tif'][0:nr_img]
            in_out_file_pairs_spark = [(f.as_posix(), out_dir_spark + f.stem+'_NDVI.png') for f in s2_data_dir.iterdir() if f.suffix == '.tif'][0:nr_img]
            print(in_out_file_pairs_dask)
            print(in_out_file_pairs_spark)

            # Dask Run
            # Setup cluster
            cluster = LocalCluster(processes=True, 
                                n_workers=nr_worker, 
                                threads_per_worker=1, 
                                local_directory='./dask-worker-space')
            client = Client(cluster)
            print(cluster)
            # Pipeline run for NDVI
            futures = []
            for f in in_out_file_pairs_dask:
                future = client.submit(export_ndvi, f)
                futures.append(future)
            t0 = time.time()
            results = client.gather(futures)
            t1 = time.time() - t0
            # Shutdown
            client.close()
            cluster.close()
            # Recording time
            time_dask.append(t1)

            # Spark Run
            # Setup SparkContext
            sc = SparkContext(master="local[{}]".format(nr_worker))
            task = sc.parallelize(in_out_file_pairs_spark)
            # Pipeline run for NDVI
            t0 = time.time()
            task.map(export_ndvi).collect()
            t1 = time.time() - t0
            SparkContext.stop(sc)
            # Recording time
            time_spark.append(t1)

        # Make image of processing time
        plt.figure('time')
        plt.plot(list_nr_img, time_dask, label='Dask, {} workers'.format(nr_worker))
        plt.plot(list_nr_img, time_spark, label='Spark, {} workers'.format(nr_worker))
    
    # Save figures
    plt.figure('time')
    plt.legend()
    plt.xlabel('Number of input images')
    plt.ylabel('Wall time (sec)')
    plt.savefig(output_dir_time+'walltime_{}.png'.format(time.clock()))


            
    