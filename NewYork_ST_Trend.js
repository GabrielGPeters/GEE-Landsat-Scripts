// imports
var Landsat8 = ee.ImageCollection("LANDSAT/LC08/C02/T1_L2"),
    Landsat7 = ee.ImageCollection("LANDSAT/LE07/C02/T2_L2"),
    Landsat5 = ee.ImageCollection("LANDSAT/LT05/C02/T1_L2"),
    Landsat4 = ee.ImageCollection("LANDSAT/LT04/C02/T1_L2");


/**
 * 
 * Author:          Gabriel Peters, ugrad (ggp2366@rit.edu)
 * Latest Version:  0.2.0, 2022-11-21
 * Affiliation:     CIS, Rochester Institute of Technology
 *
 * Purpose:         Gathers and plots surface temperature data from Landsat 4-7 
 *                  from 1982 to present over the state of New York.
 * 
 */
 
/*
     ----------------- Collecting Data ------------------
*/
 // load US states dataset and isolating New York
var stateData = ee.FeatureCollection('TIGER/2018/States');
var NewYork = stateData.filter(ee.Filter.eq('NAME', 'New York'));

// print new "NewYork" object and explorer features and properties
print(NewYork);

// add New York outline to the Map as a layer
Map.centerObject(NewYork, 6);
Map.addLayer(NewYork);

// filtering the Landsat 8 image collection
var Landsat_8 = Landsat8
              .filterDate('2013-1-1', '2022-7-1')
              .filterMetadata('CLOUD_COVER', 'less_than', 10);
              
// filtering the Landsat 7 image collection
var Landsat_7 = Landsat7
              .filterDate('1999-7-2', '2022-11-18')
              .filterMetadata('CLOUD_COVER', 'less_than', 10);

// filtering the Landsat 5 image collection
var Landsat_5 = Landsat5
              .filterDate('1984-7-2', '1999-7-1')
              .filterMetadata('CLOUD_COVER', 'less_than', 10);
              
// filtering the Landsat 4 image collection
var Landsat_4 = Landsat4
              .filterDate('1982-7-2', '1984-7-1')
              .filterMetadata('CLOUD_COVER', 'less_than', 10);
              
// print size of collection to console
print('Landsat8 collection size: ', Landsat_8.size());
print('Landsat7 collection size: ', Landsat_7.size());
print('Landsat5 collection size: ', Landsat_5.size());
print('Landsat4 collection size: ', Landsat_4.size());

// select only the surface temperature band
var STB10 = Landsat_8.select('ST_B10');
var L7STB6 = Landsat_7.select('ST_B6');
var L5STB6 = Landsat_5.select('ST_B6');
var L4STB6 = Landsat_4.select('ST_B6');

// scale to Fahrenheit, set image acquisition time
var STB10_F = STB10.map(function(img) {
  return img
    .multiply(0.00341802)
    .add(149.0)
    .subtract(273)
    .multiply(1.8)
    .add(32)
    .copyProperties(img, ['system:time_start']);
});

// scale to Kelvin, set image acquisition time
var STB10_K = STB10.map(function(img) {
  return img
    .multiply(0.00341802)
    .add(149.0)
    .copyProperties(img, ['system:time_start']);
});
var L7STB6_K = L7STB6.map(function(img) {
  return img
    .multiply(0.00341802)
    .add(149.0)
    .copyProperties(img, ['system:time_start']);
});
var L5STB6_K = L5STB6.map(function(img) {
  return img
    .multiply(0.00341802)
    .add(149.0)
    .copyProperties(img, ['system:time_start']);
});
var L4STB6_K = L4STB6.map(function(img) {
  return img
    .multiply(0.00341802)
    .add(149.0)
    .copyProperties(img, ['system:time_start']);
});

// merging image collections 
var merged = L4STB6_K.merge(L5STB6_K.merge(L7STB6_K));

/*
     ----------------- Making a Chart ------------------
*/

// chart time series of surface temperature
var ts1 = ui.Chart.image.series({
  imageCollection: merged,
  region: NewYork,
  reducer: ee.Reducer.mean(),
  scale: 200,
  xProperty: 'system:time_start'
  })
  .setOptions({
     title: 'STB10_K New York Time Series (1984-2021)',
     vAxis: {title: 'ST Kelvin'},
     lineWidth: 1.5,
     colors: ['red'],
  });
print(ts1);

// calculate mean surface temperature for New York in date range
var clipped = merged.mean().clip(NewYork);

/*
     ----------------- Adding Map Layers ------------------
*/

// add clipped image layer to the map.
Map.addLayer(clipped, {
  min: 283, max: 300,
  palette: ['black', 'blue', 'limegreen', 'yellow', 'orange', 'red', 'darkred', 'white']},
  'Mean temperature (2013-2021');


// Load Landsat image collection.
var allImages = Landsat_8
 // Select 3-band imagery for the video.
 .select(['ST_B10'])
 // Make the data 8-bit.
 .map(function(image) {
  return image.multiply(512).uint8();
 });
 
var finalVis = {min: 283, max: 300, palette: ['black', 'blue', 'limegreen', 'yellow', 'orange', 'red', 'darkred', 'white']};
function Func(image) {
  return image.visualize(finalVis);
}

var finalImage = allImages.map(Func);

Export.video.toDrive({
 collection: finalImage,
 // Name of file.
 description: 'NY_ST_Timelapse',
 folder: 'GEETimeLapses',
 // Quality of video.
 dimensions: 240,
 // FPS of video.
 framesPerSecond: 100,
 maxFrames: 200000,
 // Region of export.
 region: NewYork
});

