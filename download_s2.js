/**
 * Function to mask clouds using the Sentinel-2 QA band
 * @param {ee.Image} image Sentinel-2 image
 * @return {ee.Image} cloud masked Sentinel-2 image
 */
function maskS2clouds(image) {
    var qa = image.select('QA60');
  
    // Bits 10 and 11 are clouds and cirrus, respectively.
    var cloudBitMask = 1 << 10;
    var cirrusBitMask = 1 << 11;
  
    // Both flags should be set to zero, indicating clear conditions.
    var mask = qa.bitwiseAnd(cloudBitMask).eq(0)
        .and(qa.bitwiseAnd(cirrusBitMask).eq(0));
  
    return image.updateMask(mask).divide(10000);
  }

var poly_test = ee.Geometry.Rectangle([4.2346171335651706,51.944589555395,4.324567695088608,51.989855970508636]);

var s2 = ee.ImageCollection('COPERNICUS/S2')
        .filterDate('2018-01-01', '2019-12-01')
        .filterBounds(poly_test)
        .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20))
        .map(maskS2clouds);
print(s2);

var batch = require('users/fitoprincipe/geetools:batch')
batch.Download.ImageCollection.toDrive(s2, 'Folder', 
                {scale: 10, 
                region: poly_test, 
                type: 'float'})

var rgbVis = {
min: 0.0,
max: 0.3,
bands: ['B4', 'B8', 'B2'],
};

Map.setCenter(4.2, 52.00, 12);
Map.addLayer(s2.median(), rgbVis, 'RGB');
