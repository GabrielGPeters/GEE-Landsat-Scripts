/**
 * 
 * Author:          Gabriel Peters, ugrad (ggp2366@rit.edu)
 * Latest Version:  0.1.3
 * Affiliation:     CIS, Rochester Institute of Technology
 *
 */

//IMPORTS
var Landsat9 = ee.ImageCollection("LANDSAT/LC09/C02/T1_TOA"),
    Landsat8 = ee.ImageCollection("LANDSAT/LC08/C02/T1_TOA"),
    area = 
    /* color: #d63000 */
    /* displayProperties: [
      {
        "type": "rectangle"
      }
    ] */
    ee.Geometry.Polygon(
        [[[-3.5892241659601254, 30.450062187784255],
          [-3.5892241659601254, 11.312148657328228],
          [32.047677689508625, 11.312148657328228],
          [32.047677689508625, 30.450062187784255]]], null, false);

// filtering the Landsat 9 image collection
var Landsat_9 = Landsat9
              .filterDate('2021-12-1', '2022-7-6')
              .filterMetadata('CLOUD_COVER', 'less_than', 20)
              .filterBounds(area);

// filtering the Landsat 8 image collection
var Landsat_8 = Landsat8
              .filterDate('2021-12-1', '2022-7-6')
              .filterMetadata('CLOUD_COVER', 'less_than', 20)
              .filterBounds(area);

// print size to console
print('Filtered Image Collections: ');
print('Landsat9: ', Landsat_9.size());
print('Landsat8: ', Landsat_8.size());

// show image collections on the map
Map.addLayer(
    Landsat_9,
    {min:0, max:0.5, bands:['B1']},
    'Landsat9_B1'
  );

Map.addLayer(
    Landsat_8,
    {min:0, max:0.5, bands:['B1']},
    'Landsat8_B1'
  );

Map.centerObject(area, 5);

//     ----------------- Landsat 9 ------------------

// converting the collection to a list 
var L9CollectionList = Landsat_9.toList(Landsat_9.size());

// making a list of sequenced numbers to later fill in
var Landsat9List = ee.List.sequence(0, Landsat_9.size().subtract(1));

// function to map over "Landsat9List"
var func = function(number) {
  var index = Landsat9List.get(number);
  return ee.Number(number).subtract(number)
         .add(
           ee.Number(ee.Image(L9CollectionList.get(index))
    .select("B1")
    .reduceRegion({
          reducer: ee.Reducer.mean().unweighted(),
          geometry: area,
          maxPixels: 1e15
          })
    .get("B1"))
           );
};

// mapping function over list to get the band 1 values from 
// all the images and put them in a list
var Landsat9Values = ee.Array(Landsat9List.map(func));
//print('Landsat9Values: ', Landsat9Values);

//     ----------------- Landsat 8 ------------------

// converting the collection to a list
var L8CollectionList = Landsat_8.toList(Landsat_8.size());

// making a list of sequenced numbers to later fill in
var Landsat8List = ee.List.sequence(0, Landsat_8.size().subtract(1));

// function to map over "Landsat8List"
var func = function(number) {
  var index = Landsat8List.get(number);
  return ee.Number(number).subtract(number)
         .add(
           ee.Number(ee.Image(L8CollectionList.get(index))
    .select("B1")
    .reduceRegion({
          reducer: ee.Reducer.mean().unweighted(),
          geometry: area,
          maxPixels: 1e15
          })
    .get("B1"))
           );
};

// mapping function over list to get the band 1 values from 
// all the images and put them in a list
var Landsat8Values = ee.Array(Landsat8List.map(func));
// print('Landsat8Values: ', Landsat8Values);

//     ----------------- Plotting ------------------

// isolating band 1
var L9B1 = Landsat_9.select('B1');
var L8B1 = Landsat_8.select('B1');

// plotting functions
function func9(image) {
  var b1 = image.select('B1'); 
  return image.addBands(b1.rename('L9_B1'));
}
function func8(image) {
  var b1 = image.select('B1'); 
  return image.addBands(b1.rename('L8_B1'));
}

// mapping functions over image collections
var dataL9 = Landsat_9.map(func9);
var dataL8 = Landsat_8.map(func8);

// merge the collections
var merged = dataL9.select('L9_B1').merge(dataL8.select('L8_B1'));

// making combined collection chart
print(ui.Chart.image
  .series({
    imageCollection: merged,
    region: area,
    reducer: ee.Reducer.mean().unweighted(),
    scale: 5000
  })
  .setOptions({
          title: 'Average Landsat 8/9 B1 Pixel Values Since December 2021',
          hAxis: {title: 'Date', titleTextStyle: {italic: false, bold: true}, 
            viewWindow: {min: 1638316800000, max: 1654560000000}
          },
          vAxis: {title: 'TOA Reflectance',titleTextStyle: {italic: false, bold: true}, 
            viewWindow: {min: 0.14, max: 0.26}},
          lineWidth: 0,
          colors: ['f0af07', '76b349'],
          pointSize: 0.5,
          opacity: 0.1,
          trendlines: {
            0: {  // add a trend line to the 1st series
              type: 'linear',  // or 'polynomial', 'exponential'
              color: 'orange',
              pointSize: 0,
              lineWidth: 2,
              opacity: 1,
              visibleInLegend: false,
              },
            1: {  // add a trend line to the 2nd series
              type: 'linear',
              color: 'green',
              pointSize: 0,
              lineWidth: 2,
              opacity: 1,
              visibleInLegend: false,
              }
          }
          })
  
);

//     ------ making list of values to fill in datatable -------

// Landsat 9 Dates
var datesFunc1 = Landsat_9.map(function(image) {
  return image.set('date', image.date());
});

// Get a list of the dates.
var L9ListDates = datesFunc1.aggregate_array('date');
print('L9ListDates', L9ListDates);

// Landsat 9 Band 1
var L9B1PreList = ee.List.sequence(0, Landsat_9.size().subtract(1));

var funcL9B1 = function(number) {
  var index = L9B1PreList.get(number);
  return ee.Number(number).subtract(number)
         .add(
           ee.Number(ee.Image(L9CollectionList.get(index))
    .select("B1")
    .reduceRegion({
          reducer: ee.Reducer.mean().unweighted(),
          geometry: area,
          maxPixels: 1e15
          })
    .get("B1"))
           );
};
var L9B1List = ee.List(L9B1PreList.map(funcL9B1));
print('L9B1', L9B1List);

// Landsat 9 Band 2
var L9B2PreList = ee.List.sequence(0, Landsat_9.size().subtract(1));

var funcL9B2 = function(number) {
  var index = L9B2PreList.get(number);
  return ee.Number(number).subtract(number)
         .add(
           ee.Number(ee.Image(L9CollectionList.get(index))
    .select("B2")
    .reduceRegion({
          reducer: ee.Reducer.mean().unweighted(),
          geometry: area,
          maxPixels: 1e15
          })
    .get("B2"))
           );
};
var L9B2List = ee.List(L9B2PreList.map(funcL9B2));
print('L9B2', L9B2List);

// Landsat 8 Dates
var datesFunc2 = Landsat_8.map(function(image) {
  return image.set('date', image.date());
});

// Get a list of the dates.
var L8ListDates = datesFunc2.aggregate_array('date');
print('L8ListDates', L8ListDates);

// Landsat 8 Band 1
var L8B1PreList = ee.List.sequence(0, Landsat_8.size().subtract(1));

var funcL8B1 = function(number) {
  var index = L8B1PreList.get(number);
  return ee.Number(number).subtract(number)
         .add(
           ee.Number(ee.Image(L8CollectionList.get(index))
    .select("B1")
    .reduceRegion({
          reducer: ee.Reducer.mean().unweighted(),
          geometry: area,
          maxPixels: 1e15
          })
    .get("B1"))
           );
};
var L8B1List = ee.List(L8B1PreList.map(funcL8B1));
print('L8B1', L8B1List);

// Landsat 8 Band 2
var L8B2PreList = ee.List.sequence(0, Landsat_8.size().subtract(1));

var funcL8B2 = function(number) {
  var index = L8B2PreList.get(number);
  return ee.Number(number).subtract(number)
         .add(
           ee.Number(ee.Image(L8CollectionList.get(index))
    .select("B2")
    .reduceRegion({
          reducer: ee.Reducer.mean().unweighted(),
          geometry: area,
          maxPixels: 1e15
          })
    .get("B2"))
           );
};
var L8B2List = ee.List(L8B2PreList.map(funcL8B2));
print('L8B2', L8B2List);

//     ----------------- Making Downloadable (Testing) ------------------

/*
var L9Size = ee.Number(L9B1List.size().getInfo());
var L8Size = ee.Number(L8B1List.size().getInfo());

if (L9Size >= L8Size) { 
  var ListSize = L9Size;
} else if (L9Size > L8Size) {
  var ListSize = L8Size;
}

var dataTable = {
  cols: [{id: 'L9B1', label: 'L9B1', type: 'number'},
         {id: 'L9B2', label: 'L9B2', type: 'number'},
         ],
  rows: [
         {c: [{v: L9B1List.get(0).getInfo()}, {v: L8B1List.get(0).getInfo()}]},
         {c: [{v: L9B1List.get(1).getInfo()}, {v: L8B1List.get(1).getInfo()}]},
         {c: [{v: L9B1List.get(2).getInfo()}, {v: L8B1List.get(2).getInfo()}]},
         {c: [{v: L9B1List.get(3).getInfo()}, {v: L8B1List.get(3).getInfo()}]},
         {c: [{v: L9B1List.get(4).getInfo()}, {v: L8B1List.get(4).getInfo()}]},
         {c: [{v: L9B1List.get(5).getInfo()}, {v: L8B1List.get(5).getInfo()}]},
         {c: [{v: L9B1List.get(6).getInfo()}, {v: L8B1List.get(6).getInfo()}]},
         {c: [{v: L9B1List.get(7).getInfo()}, {v: L8B1List.get(7).getInfo()}]},
         {c: [{v: L9B1List.get(8).getInfo()}, {v: L8B1List.get(8).getInfo()}]},
         {c: [{v: L9B1List.get(9).getInfo()}, {v: L8B1List.get(9).getInfo()}]},
         {c: [{v: L9B1List.get(10).getInfo()}, {v: L8B1List.get(10).getInfo()}]},
         {c: [{v: 'NA'}, {v: L8B1List.get(11).getInfo()}]},
         {c: [{v: 'NA'}, {v: L8B1List.get(12).getInfo()}]},

        ]
};



var chart = ui.Chart(dataTable).setChartType('Table');
print(chart);
chart.setDownloadable('CSV');
print('Chart is downloadable as: ', chart.getDownloadable());

*/

