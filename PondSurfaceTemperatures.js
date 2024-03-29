/**
 * 
 * Author:         Gabriel Peters, ugrad (ggp2366@rit.edu)
 * Latest Version:  0.2.0 (Updated: 8-10-22) 
 * Affiliation:    CIS, Rochester Institute of Technology
 *
 */
 
//     ------------------- READ ME ------------------

/*
 *  Important info: 
 *  1. This code is designed to provide estimated surface temperature data
 *     from Landsat 9 Level 2 data, for a specific set of manually selected 
 *     coordinates
 *  2. Each section of the code is collapsable, click the arrow by the code
 *     line under each title to view
 *  3. Verbose settings are utilized to make the output easy to understand.
 *     To see fine details set these settings to "true"
 *  
 *
 */

// Verbose settings:

var Verbose = false;

var Console = false;

//     ----------- Defining TidbiT Geometry ----------

// Define a Point object.
var point1 = ee.Geometry.Point(-76.1646402, 43.6596454); // #1148
var point2 = ee.Geometry.Point(-76.1776992, 43.6428234); // #5977
var point3 = ee.Geometry.Point(-76.1669502, 43.6500498); // #5967
var point4 = ee.Geometry.Point(-76.1839152, 43.6623287); // #3513
var point5 = ee.Geometry.Point(-76.1880032, 43.6675437); // #3515

// Print the result to the console.
  
if (Console === true){
  print('Tidbit Coordinates: ');
  print('var point1 = (-76.1646402, 43.6596454)');
  print('var point2 = (-76.1776992, 43.6428234)');
  print('var point3 = (-76.1669502, 43.6500498)');
  print('var point4 = (-76.1839152, 43.6623287)');
  print('var point5 = (-76.1880032, 43.6675437)');
}

Map.addLayer(point1,
             {'color': 'red'},
             'Geometry [red]: point1');
             
Map.addLayer(point2,
             {'color': 'green'},
             'Geometry [green]: point2');

Map.addLayer(point3,
             {'color': 'blue'},
             'Geometry [blue]: point3');

Map.addLayer(point4,
             {'color': 'yellow'},
             'Geometry [yellow]: point4');

Map.addLayer(point5,
             {'color': 'black'},
             'Geometry [black]: point5');
             


Map.centerObject(point4, 13);

//     --------------- Making a Legend ---------------

// set position of panel
var legend = ui.Panel({
  style: {
    position: 'bottom-left',
    padding: '8px 15px'
  }
});
 
// Create legend title
var legendTitle = ui.Label({
  value: 'TidbiT Legend',
  style: {
    fontSize: '18px',
    margin: '0 0 4px 0',
    padding: '0'
    }
});
 
// Add the title to the panel
legend.add(legendTitle);
 
// Creates and styles 1 row of the legend.
var makeRow = function(color, name) {
 
      // Create the label that is actually the colored box.
      var colorBox = ui.Label({
        style: {
          backgroundColor: '#' + color,
          // Use padding to give the box height and width.
          padding: '8px',
          margin: '0 0 4px 0'
        }
      });
 
      // Create the label filled with the description text.
      var description = ui.Label({
        value: name,
        style: {margin: '0 0 4px 6px'}
      });
 
      // return the panel
      return ui.Panel({
        widgets: [colorBox, description],
        layout: ui.Panel.Layout.Flow('horizontal')
      });
};
 
//  Palette with the colors
var palette =['FF0000', '22ff00', '1500ff', 'FFFF00', '000000'];
 
// name of the legend
var names = ['#1148 Depth: 1in','#5977 Depth: 16in','#5967 Depth: 16in',
             '#3513 Depth: 19in','#3515 Depth: 13in'];
 
// Add color and and names
for (var i = 0; i < 5; i++) {
  legend.add(makeRow(palette[i], names[i]));
  }  
 
// add legend to map (alternatively you can also print the legend to the console)
Map.add(legend);


//     ------------ Filtering Collection -------------

//Imports
var Landsat9_C2_T1_L2 = ee.ImageCollection("LANDSAT/LC09/C02/T1_L2");

// Create an image collection from surface reflectance dataset consisting of only images from days that had sampling occur somewhere

print('Images found...', Landsat9_C2_T1_L2.size());
print('--------------------------------------------------');

var imageCollection = ee.ImageCollection("LANDSAT/LC09/C02/T1_L2")
              .filterDate('2022-6-28', '2022-7-10')
              .filterMetadata('CLOUD_COVER', 'less_than', 20)
              .filterBounds(point1);

print('Filtered Over Region: ', imageCollection.size());

if (Verbose === true){
  Map.addLayer(
    Landsat9_C2_T1_L2,
    {min:0, max:65535, bands:['ST_B10']},
    'Cloud Filter'
  );
}

//  setting image variable:
//var image = ee.Image( INSERT PRODUCT ID );        // get specific image
var image = ee.Image(imageCollection.first());

// Get the timestamp and convert it to a date.
var date = (ee.Date(image.get('system:time_start')).format('YYYY-MM-dd')).getInfo();  
if (Console === true){
  print('Timestamp:', date); 
}
// setting surface temperature variable
var ST_b10 = image.select('ST_B10');

var image1 = ee.Image(image);

if (Verbose === true){
  Map.addLayer(               // adding map layer for surface temp image
      image,
      {min:0, max:65535, bands:['ST_B10']},
      'ST_B10'
    );
}

//   ------------ Extracting Pixel Values ------------

// extract the pixel value for point1
var data = image
.select("ST_B10")
.reduceRegion(ee.Reducer.first(),point1,10)
.get("ST_B10")

// convert to number
var dataN = ee.Number(data);

var scaleFactor = 0.00341802;
var constant = 149.0;

print('--------------------------------------------------');

if (Console === true){
  print('Point1 (Dock): ');

  // pixel value
  print('Pixel Value: ', dataN);
}

// pixel value in Kelvin
var surfTemp = dataN.multiply(scaleFactor).add(constant);

if (Console === true){
  print('Pixel Value (Kelvin): ', surfTemp);
}

// pixel value in Celcius
var surfTempF = surfTemp.subtract(273);

if (Console === true){
  print('Pixel Value (Celcius): ', surfTempF);

  print('--------------------------------------------------');
  print('Point2 (Wigwam): ');
}

// extract the pixel value for point2
var data2 = image
.select("ST_B10")
.reduceRegion(ee.Reducer.first(),point2,10)
.get("ST_B10");

// convert to number
var dataN2 = ee.Number(data2);

if (Console === true){
  // pixel value
  print('Pixel Value: ', dataN2);
}

// pixel value in Kelvin
var surfTemp2 = dataN2.multiply(scaleFactor).add(constant);

if (Console === true){
  print('Pixel Value (Kelvin): ', surfTemp2);
} 

// pixel value in Celcius
var surfTempF2 = surfTemp2.subtract(273);

if (Console === true){
  print('Pixel Value (Celcius): ', surfTempF2);

  print('--------------------------------------------------');
  print('Point3 (Seber): ');
}

// extract the pixel value for point3
var data3 = image
.select("ST_B10")
.reduceRegion(ee.Reducer.first(),point3,10)
.get("ST_B10");

// convert to number
var dataN3 = ee.Number(data3);

if (Console === true){
  // pixel value
  print('Pixel Value: ', dataN3);
}

// pixel value in Kelvin
var surfTemp3 = dataN3.multiply(scaleFactor).add(constant);

if (Console === true){
  print('Pixel Value (Kelvin): ', surfTemp3);
}

// pixel value in Celcius
var surfTempF3 = surfTemp3.subtract(273);

if (Console === true){
  print('Pixel Value (Celcius): ', surfTempF3);

  print('--------------------------------------------------');
  print('Point4 (South Carl): ');
}

// extract the pixel value for point4
var data4 = image
.select("ST_B10")
.reduceRegion(ee.Reducer.first(),point4,10)
.get("ST_B10");

// convert to number
var dataN4 = ee.Number(data4);

if (Console === true){
  // pixel value
  print('Pixel Value: ', dataN4);
}

// pixel value in Kelvin
var surfTemp4 = dataN4.multiply(scaleFactor).add(constant);

if (Console === true){
  print('Pixel Value (Kelvin): ', surfTemp4);
}

// pixel value in Celcius
var surfTempF4 = surfTemp4.subtract(273);

if (Console === true){
  print('Pixel Value (Celcius): ', surfTempF4);

  print('--------------------------------------------------');
  print('Point5 (North Carl): ');
}

// extract the pixel value for point5
var data5 = image
.select("ST_B10")
.reduceRegion(ee.Reducer.first(),point5,10)
.get("ST_B10");

// convert to number
var dataN5 = ee.Number(data5);

if (Console === true){
  // pixel value
  print('Pixel Value: ', dataN5);
}

// pixel value in Kelvin
var surfTemp5 = dataN5.multiply(scaleFactor).add(constant);

if (Console === true){
  print('Pixel Value (Kelvin): ', surfTemp5);
}

// pixel value in Celcius
var surfTempF5 = surfTemp5.subtract(273);

if (Console === true){
  print('Pixel Value (Celcius): ', surfTempF5);
}

//   -------------- Making a Data Table --------------

// type conversion for table
var value1 = dataN.getInfo();
var value2 = dataN2.getInfo();
var value3 = dataN3.getInfo();
var value4 = dataN4.getInfo();
var value5 = dataN5.getInfo();
var SurfTemp1 = surfTemp.getInfo();
var SurfTemp2 = surfTemp2.getInfo();
var SurfTemp3 = surfTemp3.getInfo();
var SurfTemp4 = surfTemp4.getInfo();
var SurfTemp5 = surfTemp5.getInfo();
var SurfTempF1 = surfTempF.getInfo();
var SurfTempF2 = surfTempF2.getInfo();
var SurfTempF3 = surfTempF3.getInfo();
var SurfTempF4 = surfTempF4.getInfo();
var SurfTempF5 = surfTempF5.getInfo();
var time = (ee.Date(image.get('system:time_start')).format('H:m:s')).getInfo();

print('Data Table:');

var dataTable = [
  ['TidbiT', 'Location (Sandy Pond)', 'Pixel Value', 'Kelvin (K)', 'Celcius (C)', '(year-month-day hour:minute:second)'],
  ['#1148', '(-76.1646402, 43.6596454)', value1, SurfTemp1, SurfTempF1, date + ' ' + time],
  ['#5977', '(-76.1776992, 43.6428234)', value2, SurfTemp2, SurfTempF2, date + ' ' + time],
  ['#5967', '(-76.1669502, 43.6500498)', value3, SurfTemp3, SurfTempF3, date + ' ' + time],
  ['#3513', '(-76.1839152, 43.6623287)', value4, SurfTemp4, SurfTempF4, date + ' ' + time],
  ['#3515', '(-76.1880032, 43.6675437)', value5, SurfTemp5, SurfTempF5, date + ' ' + time],
];

var chart = ui.Chart(dataTable).setChartType('Table');
print(chart);
chart.setDownloadable('CSV');
print('Chart is downloadable as: ', chart.getDownloadable());

//   ------------------- Exporting -------------------

/*
var date = (ee.Date(image.get('system:time_start')).format('YYYY-MM-dd')).getInfo();  
var image_id = (image.getString('LANDSAT_PRODUCT_ID')).getInfo();
var imageIndexId = (image.getString('system:index')).getInfo();
print('Name of export: ' + '"' + image_id  +  '"');
print('Image id: ' + image_id);
print('Image Index: ' + 'LANDSAT/LC09/C02/T1_L2/' + imageIndexId);

// exporting band 10 surface temperature IMAGE
Export.image.toDrive({    
  image: ST_b10,
  folder: 'Landsat9: ' + date, // folder in your google drive
  description: 'B10_Surface_Temp',
  fileNamePrefix: 'B10 Surface Temp',     // name of file will be the date the image was taken
  scale: 50,
  maxPixels: 10000000000000
  });
  */

