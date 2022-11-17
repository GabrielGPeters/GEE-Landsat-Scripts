# Imports
import ee
import csv
from termcolor import colored
import time
import math
from multiprocessing import Process


# initializing the library
ee.Initialize()

'''
    author::        
        Gabriel Peters, ugrad (ggp2366@rit.edu)
    copyright::     
        Copyright (C) 2022, Rochester Institute of Technology
    version::       
        1.1.5
    disclaimer::
        This source code is provided "as is" and without warranties as to 
        performance or merchantability. The author and/or distributors of 
        this source code may have made statements about this source code. 
        Any such statements do not constitute warranties and shall not be 
        relied on by the user in deciding whether to use this source code.
      
        This source code is provided without any express or implied warranties 
        whatsoever. Because of the diversity of conditions and hardware under 
        which this source code may be used, no warranty of fitness for a 
        particular purpose is offered. The user is advised to test the source 
        code thoroughly before relying on it. The user must assume the entire 
        risk of using the source code.
    Purpose::
        1. This code is designed to provide estimated surface temperature data
           from Landsat 9 Level 2 images, Band 11 and Band 10 radiance data from 
           Landsat 8/9 Collection 2 Level 1 images, for a specific set of manually selected
           coordinates 
        2. Data is written into separate CSV files for each location
'''

#point1 = ee.Geometry.Point([-74.8930, 42.7649])         # Otsego Lake
#name1 = "Otsego"
#point2 = ee.Geometry.Point([-112.2818, 33.8759])        # Lake Pleasant
#name2 = "Pleasant"
#point3 = ee.Geometry.Point([-111.5291, 33.5721])        # Saguaro Lake
#name3 = "Saguaro"
#point4 = ee.Geometry.Point([-111.4302, 33.5396])        # Canyon Lake
#name4 = "Canyon"
#point5 = ee.Geometry.Point([-111.6303, 33.8322])        # Bartlett Reservoir
#name5 = "Barlett"
point1 = ee.Geometry.Point([-120.01184, 39.178263])    # Lake Tahoe
name1 = "Tahoe"
point2 = ee.Geometry.Point([-115.82425, 33.22532])     # Salton Sea
name2 = "Salton"
point3 = ee.Geometry.Point([-116.01947, 36.62373])     # Desert Rock
name3 = "Desert"
point4 = ee.Geometry.Point([-105.1017, 48.30783])      # Fort Peck
name4 = "Peck"
point5 = ee.Geometry.Point([-96.62328, 43.73403])      # Sioux Falls
name5 = "Sioux"
point6 = ee.Geometry.Point([-89.8729, 34.2547])        # Goodwin Creek
name6 = "Goodwin"

Landsat9_C2_T1_L2 = ee.ImageCollection("LANDSAT/LC09/C02/T1_L2")

def function1():
    imageCollection1 = ee.ImageCollection("LANDSAT/LC09/C02/T1_L2") \
        .filterDate('2021-12-1', '2022-10-11') \
        .filterBounds(point1)
    imageList1 = imageCollection1.toList(imageCollection1.size())
    imageCollection1_8 = ee.ImageCollection("LANDSAT/LC08/C02/T1_L2") \
        .filterDate('2021-12-1', '2022-10-11') \
        .filterBounds(point1)
    imageList1_8 = imageCollection1_8.toList(imageCollection1_8.size())
    imageCollection1_2 = ee.ImageCollection("LANDSAT/LC09/C02/T1") \
        .filterDate('2021-12-1', '2022-10-11') \
        .filterBounds(point1)
    imageList1_2 = imageCollection1_2.toList(imageCollection1_2.size())
    imageCollection1_3 = ee.ImageCollection("LANDSAT/LC08/C02/T1") \
        .filterDate('2021-12-1', '2022-10-11') \
        .filterBounds(point1)
    imageList1_3 = imageCollection1_3.toList(imageCollection1_3.size())
    c1Size = min([imageCollection1_2.size().getInfo(), imageCollection1_3.size().getInfo(), imageCollection1.size().getInfo()])

    scaleFactor = 0.00341802
    constant = 149.0
    list1 = [["LongLat", "Date L9IM","L9ST [Kelvin]","L9B10 [radiance units]", "L9B11 [radiance units]", "L9 Product ID", "L9 Scene ID", "Date L8IM","L8ST [Kelvin]", "L8B10 [radiance units]", "L8B11 [radiance units]", "L8 Product ID", "L8 Scene ID"]]
    #print('Filtered Over ' + name1 +': ', c1Size)
    print("Computing " + name1 + " Data...")

    for i in range(c1Size):
        image1 = ee.Image(imageList1.get(i))
        image1_8 = ee.Image(imageList1_8.get(i))
        image1_2 = ee.Image(imageList1_2.get(i))
        image1_3 = ee.Image(imageList1_3.get(i))
        b10_2 = ee.Number(image1_2.select('B10').reduceRegion(ee.Reducer.first(), point1, 5).get('B10')).getInfo()
        b11_2 = ee.Number(image1_2.select('B11').reduceRegion(ee.Reducer.first(), point1, 5).get('B11')).getInfo()
        if b10_2 is None:
            text = colored(f'{name1} CSV failed at index {i}', "red", attrs=["reverse", "blink"])
            print(text)
            break
        b10L8_2 = ee.Number(image1_3.select('B10').reduceRegion(ee.Reducer.first(), point1, 5).get('B10')).getInfo()
        b11L8_2 = ee.Number(image1_3.select('B11').reduceRegion(ee.Reducer.first(), point1, 5).get('B11')).getInfo()
        RADIANCE_MULT_BAND_10 = image1_2.get('RADIANCE_MULT_BAND_10').getInfo()
        RADIANCE_MULT_BAND_11 = image1_2.get('RADIANCE_MULT_BAND_11').getInfo()
        RADIANCE_ADD_BAND_10 = image1_2.get('RADIANCE_ADD_BAND_10').getInfo()
        RADIANCE_ADD_BAND_11 = image1_2.get('RADIANCE_ADD_BAND_11').getInfo()
        b10_radiance = b10_2 * RADIANCE_MULT_BAND_10 + RADIANCE_ADD_BAND_10
        b11_radiance = b11_2 * RADIANCE_MULT_BAND_11 + RADIANCE_ADD_BAND_11
        RADIANCE_MULT_BAND_10L8 = image1_3.get('RADIANCE_MULT_BAND_10').getInfo()
        RADIANCE_MULT_BAND_11L8 = image1_3.get('RADIANCE_MULT_BAND_11').getInfo()
        RADIANCE_ADD_BAND_10L8 = image1_3.get('RADIANCE_ADD_BAND_10').getInfo()
        RADIANCE_ADD_BAND_11L8 = image1_3.get('RADIANCE_ADD_BAND_11').getInfo()
        b10_radianceL8 = b10L8_2 * RADIANCE_MULT_BAND_10L8 + RADIANCE_ADD_BAND_10L8
        b11_radianceL8 = b11L8_2 * RADIANCE_MULT_BAND_11L8 + RADIANCE_ADD_BAND_11L8
        date1 = (ee.Date(image1.get('system:time_start')).format('YYYY-MM-dd')).getInfo()
        date1L8 = (ee.Date(image1_3.get('system:time_start')).format('YYYY-MM-dd')).getInfo()
        surfTemp = ee.Number(image1.select("ST_B10").reduceRegion(ee.Reducer.first(), point1, 5).get("ST_B10")).getInfo() * scaleFactor + constant
        surfTemp8 = ee.Number(image1_8.select("ST_B10").reduceRegion(ee.Reducer.first(), point1, 5).get("ST_B10")).getInfo() * scaleFactor + constant
        productId = (image1.getString('LANDSAT_PRODUCT_ID')).getInfo()
        sceneId = (image1.getString('LANDSAT_SCENE_ID')).getInfo()
        productIdL8 = (image1_3.getString('LANDSAT_PRODUCT_ID')).getInfo()
        sceneIdL8 = (image1_3.getString('LANDSAT_SCENE_ID')).getInfo()
        list1.append([(-74.8930, 42.7649), date1, round(surfTemp, 3), round(b10_radiance, 3), round(b11_radiance, 3), productId, sceneId, date1L8, round(surfTemp8, 3), round(b10_radianceL8, 3), round(b11_radianceL8, 3), productIdL8, sceneIdL8])
        if i==c1Size-1:
            text = colored(name1 + " CSV saved", "green", attrs=["reverse", "blink"])
            print(text)

    with open(name1 + '.csv', 'w', newline='') as file:
        writer = csv.writer(file, delimiter=',')
        writer.writerows(list1)

#################################################################################
def function2():
    imageCollection2 = ee.ImageCollection("LANDSAT/LC09/C02/T1_L2") \
        .filterDate('2021-12-1', '2022-10-11') \
        .filterBounds(point2)
    imageList2 = imageCollection2.toList(imageCollection2.size())
    imageCollection2_8 = ee.ImageCollection("LANDSAT/LC08/C02/T1_L2") \
        .filterDate('2021-12-1', '2022-10-11') \
        .filterBounds(point2)
    imageList2_8 = imageCollection2_8.toList(imageCollection2_8.size())
    imageCollection2_2 = ee.ImageCollection("LANDSAT/LC09/C02/T1") \
        .filterDate('2021-12-1', '2022-10-11') \
        .filterBounds(point2)
    imageList2_2 = imageCollection2_2.toList(imageCollection2_2.size())
    imageCollection2_3 = ee.ImageCollection("LANDSAT/LC08/C02/T1") \
        .filterDate('2021-12-1', '2022-10-11') \
        .filterBounds(point2)
    imageList2_3 = imageCollection2_3.toList(imageCollection2_3.size())
    c2Size = min([imageCollection2_2.size().getInfo(), imageCollection2_3.size().getInfo(), imageCollection2.size().getInfo()])

    scaleFactor = 0.00341802
    constant = 149.0
    list2 = [["LongLat", "Date L9IM","L9ST [Kelvin]","L9B10 [radiance units]", "L9B11 [radiance units]", "L9 Product ID", "L9 Scene ID", "Date L8IM","L8ST [Kelvin]", "L8B10 [radiance units]", "L8B11 [radiance units]", "L8 Product ID", "L8 Scene ID"]]
    #print('Filtered Over Lake Pleasant: ', c2Size)
    print("Computing " + name2 + " Data...")

    for j in range(c2Size):
        image2 = ee.Image(imageList2.get(j))
        image2_8 = ee.Image(imageList2_8.get(j))
        image2_2 = ee.Image(imageList2_2.get(j))
        image2_3 = ee.Image(imageList2_3.get(j))
        b10_2 = ee.Number(image2_2.select('B10').reduceRegion(ee.Reducer.first(), point2, 5).get('B10')).getInfo()
        b11_2 = ee.Number(image2_2.select('B11').reduceRegion(ee.Reducer.first(), point2, 5).get('B11')).getInfo()
        if b10_2 is None:
            text = colored(f'{name2} CSV failed at index {j}', "red", attrs=["reverse", "blink"])
            print(text)
            break
        b10L8_2 = ee.Number(image2_3.select('B10').reduceRegion(ee.Reducer.first(), point2, 5).get('B10')).getInfo()
        b11L8_2 = ee.Number(image2_3.select('B11').reduceRegion(ee.Reducer.first(), point2, 5).get('B11')).getInfo()
        RADIANCE_MULT_BAND_10 = image2_2.get('RADIANCE_MULT_BAND_10').getInfo()
        RADIANCE_MULT_BAND_11 = image2_2.get('RADIANCE_MULT_BAND_11').getInfo()
        RADIANCE_ADD_BAND_10 = image2_2.get('RADIANCE_ADD_BAND_10').getInfo()
        RADIANCE_ADD_BAND_11 = image2_2.get('RADIANCE_ADD_BAND_11').getInfo()
        b10_radiance = b10_2 * RADIANCE_MULT_BAND_10 + RADIANCE_ADD_BAND_10
        b11_radiance = b11_2 * RADIANCE_MULT_BAND_11 + RADIANCE_ADD_BAND_11
        RADIANCE_MULT_BAND_10L8 = image2_3.get('RADIANCE_MULT_BAND_10').getInfo()
        RADIANCE_MULT_BAND_11L8 = image2_3.get('RADIANCE_MULT_BAND_11').getInfo()
        RADIANCE_ADD_BAND_10L8 = image2_3.get('RADIANCE_ADD_BAND_10').getInfo()
        RADIANCE_ADD_BAND_11L8 = image2_3.get('RADIANCE_ADD_BAND_11').getInfo()
        b10_radianceL8 = b10L8_2 * RADIANCE_MULT_BAND_10L8 + RADIANCE_ADD_BAND_10L8
        b11_radianceL8 = b11L8_2 * RADIANCE_MULT_BAND_11L8 + RADIANCE_ADD_BAND_11L8
        date1 = (ee.Date(image2.get('system:time_start')).format('YYYY-MM-dd')).getInfo()
        date1L8 = (ee.Date(image2_3.get('system:time_start')).format('YYYY-MM-dd')).getInfo()
        surfTemp = ee.Number(image2.select("ST_B10").reduceRegion(ee.Reducer.first(), point2, 5).get("ST_B10")).getInfo() * scaleFactor + constant
        surfTemp8 = ee.Number(image2_8.select("ST_B10").reduceRegion(ee.Reducer.first(), point2, 5).get("ST_B10")).getInfo() * scaleFactor + constant
        productId = (image2.getString('LANDSAT_PRODUCT_ID')).getInfo()
        sceneId = (image2.getString('LANDSAT_SCENE_ID')).getInfo()
        productIdL8 = (image2_3.getString('LANDSAT_PRODUCT_ID')).getInfo()
        sceneIdL8 = (image2_3.getString('LANDSAT_SCENE_ID')).getInfo()
        list2.append([(-112.2818, 33.8759), date1, round(surfTemp, 3), round(b10_radiance, 3), round(b11_radiance, 3), productId, sceneId, date1L8, round(surfTemp, 3), round(b10_radianceL8, 3), round(b11_radianceL8, 3), productIdL8, sceneIdL8])
        if j==c2Size-1:
            text = colored(name2 + " CSV saved", "green", attrs=["reverse", "blink"])
            print(text)

    with open(name2 + '.csv', 'w', newline='') as file:
        writer = csv.writer(file, delimiter=',')
        writer.writerows(list2)

#################################################################################

def function3():
    imageCollection3 = ee.ImageCollection("LANDSAT/LC09/C02/T1_L2") \
        .filterDate('2021-12-1', '2022-10-11') \
        .filterBounds(point3)
    imageList3 = imageCollection3.toList(imageCollection3.size())
    imageCollection3_8 = ee.ImageCollection("LANDSAT/LC08/C02/T1_L2") \
        .filterDate('2021-12-1', '2022-10-11') \
        .filterBounds(point3)
    imageList3_8 = imageCollection3_8.toList(imageCollection3_8.size())
    imageCollection3_2 = ee.ImageCollection("LANDSAT/LC09/C02/T1") \
        .filterDate('2021-12-1', '2022-10-11') \
        .filterBounds(point3)
    imageList3_2 = imageCollection3_2.toList(imageCollection3_2.size())
    imageCollection3_3 = ee.ImageCollection("LANDSAT/LC08/C02/T1") \
        .filterDate('2021-12-1', '2022-10-11') \
        .filterBounds(point3)
    imageList3_3 = imageCollection3_3.toList(imageCollection3_3.size())
    c3Size = min([imageCollection3_2.size().getInfo(), imageCollection3_3.size().getInfo(), imageCollection3.size().getInfo()])

    scaleFactor = 0.00341802
    constant = 149.0
    list3 = [["LongLat", "Date L9IM","L9ST [Kelvin]","L9B10 [radiance units]", "L9B11 [radiance units]", "L9 Product ID", "L9 Scene ID", "Date L8IM","L8ST [Kelvin]", "L8B10 [radiance units]", "L8B11 [radiance units]", "L8 Product ID", "L8 Scene ID"]]
    #print('Filtered Over Saguaro Lake: ', c3Size)
    print("Computing " + name3 + " Data...")

    for k in range(c3Size):
        image3 = ee.Image(imageList3.get(k))
        image3_8 = ee.Image(imageList3_8.get(k))
        image3_2 = ee.Image(imageList3_2.get(k))
        image3_3 = ee.Image(imageList3_3.get(k))
        b10_2 = ee.Number(image3_2.select('B10').reduceRegion(ee.Reducer.first(), point3, 5).get('B10')).getInfo()
        b11_2 = ee.Number(image3_2.select('B11').reduceRegion(ee.Reducer.first(), point3, 5).get('B11')).getInfo()
        if b10_2 is None:
            text = colored(f'{name3} CSV failed at index {k}', "red", attrs=["reverse", "blink"])
            print(text)
            break
        b10L8_2 = ee.Number(image3_3.select('B10').reduceRegion(ee.Reducer.first(), point3, 5).get('B10')).getInfo()
        b11L8_2 = ee.Number(image3_3.select('B11').reduceRegion(ee.Reducer.first(), point3, 5).get('B11')).getInfo()
        RADIANCE_MULT_BAND_10 = image3_2.get('RADIANCE_MULT_BAND_10').getInfo()
        RADIANCE_MULT_BAND_11 = image3_2.get('RADIANCE_MULT_BAND_11').getInfo()
        RADIANCE_ADD_BAND_10 = image3_2.get('RADIANCE_ADD_BAND_10').getInfo()
        RADIANCE_ADD_BAND_11 = image3_2.get('RADIANCE_ADD_BAND_11').getInfo()
        b10_radiance = b10_2 * RADIANCE_MULT_BAND_10 + RADIANCE_ADD_BAND_10
        b11_radiance = b11_2 * RADIANCE_MULT_BAND_11 + RADIANCE_ADD_BAND_11
        RADIANCE_MULT_BAND_10L8 = image3_3.get('RADIANCE_MULT_BAND_10').getInfo()
        RADIANCE_MULT_BAND_11L8 = image3_3.get('RADIANCE_MULT_BAND_11').getInfo()
        RADIANCE_ADD_BAND_10L8 = image3_3.get('RADIANCE_ADD_BAND_10').getInfo()
        RADIANCE_ADD_BAND_11L8 = image3_3.get('RADIANCE_ADD_BAND_11').getInfo()
        b10_radianceL8 = b10L8_2 * RADIANCE_MULT_BAND_10L8 + RADIANCE_ADD_BAND_10L8
        b11_radianceL8 = b11L8_2 * RADIANCE_MULT_BAND_11L8 + RADIANCE_ADD_BAND_11L8
        date1 = (ee.Date(image3.get('system:time_start')).format('YYYY-MM-dd')).getInfo()
        date1L8 = (ee.Date(image3_3.get('system:time_start')).format('YYYY-MM-dd')).getInfo()
        surfTemp = ee.Number(image3.select("ST_B10").reduceRegion(ee.Reducer.first(), point3, 5).get("ST_B10")).getInfo() * scaleFactor + constant
        surfTemp8 = ee.Number(image3_8.select("ST_B10").reduceRegion(ee.Reducer.first(), point3, 5).get("ST_B10")).getInfo() * scaleFactor + constant
        productId = (image3.getString('LANDSAT_PRODUCT_ID')).getInfo()
        sceneId = (image3.getString('LANDSAT_SCENE_ID')).getInfo()
        productIdL8 = (image3_3.getString('LANDSAT_PRODUCT_ID')).getInfo()
        sceneIdL8 = (image3_3.getString('LANDSAT_SCENE_ID')).getInfo()
        list3.append([(-111.5291, 33.5721), date1, round(surfTemp, 3), round(b10_radiance, 3), round(b11_radiance, 3), productId, sceneId, date1L8, round(surfTemp8, 3), round(b10_radianceL8, 3), round(b11_radianceL8, 3), productIdL8, sceneIdL8])
        if k==c3Size-1:
            text = colored(name3 + " CSV saved", "green", attrs=["reverse", "blink"])
            print(text)

    with open(name3 + '.csv', 'w', newline='') as file:
        writer = csv.writer(file, delimiter=',')
        writer.writerows(list3)

#################################################################################

def function4():
    imageCollection4 = ee.ImageCollection("LANDSAT/LC09/C02/T1_L2") \
        .filterDate('2021-12-1', '2022-10-11') \
        .filterBounds(point4)
    imageList4 = imageCollection4.toList(imageCollection4.size())
    imageCollection4_8 = ee.ImageCollection("LANDSAT/LC08/C02/T1_L2") \
        .filterDate('2021-12-1', '2022-10-11') \
        .filterBounds(point4)
    imageList4_8 = imageCollection4_8.toList(imageCollection4_8.size())
    imageCollection4_2 = ee.ImageCollection("LANDSAT/LC09/C02/T1") \
        .filterDate('2021-12-1', '2022-10-11') \
        .filterBounds(point4)
    imageList4_2 = imageCollection4_2.toList(imageCollection4_2.size())
    imageCollection4_3 = ee.ImageCollection("LANDSAT/LC08/C02/T1") \
        .filterDate('2021-12-1', '2022-10-11') \
        .filterBounds(point4)
    imageList4_3 = imageCollection4_3.toList(imageCollection4_3.size())
    c4Size = min([imageCollection4_2.size().getInfo(), imageCollection4_3.size().getInfo(), imageCollection4.size().getInfo()])

    scaleFactor = 0.00341802
    constant = 149.0
    list4 = [["LongLat", "Date L9IM","L9ST [Kelvin]","L9B10 [radiance units]", "L9B11 [radiance units]", "L9 Product ID", "L9 Scene ID", "Date L8IM","L8ST [Kelvin]", "L8B10 [radiance units]", "L8B11 [radiance units]", "L8 Product ID", "L8 Scene ID"]]
    #print('Filtered Over Canyon Lake: ', c4Size)
    print("Computing " + name4 + " Data...")

    for l in range(c4Size):
        image4 = ee.Image(imageList4.get(l))
        image4_8 = ee.Image(imageList4_8.get(l))
        image4_2 = ee.Image(imageList4_2.get(l))
        image4_3 = ee.Image(imageList4_3.get(l))
        b10_2 = ee.Number(image4_2.select('B10').reduceRegion(ee.Reducer.first(), point4, 5).get('B10')).getInfo()
        b11_2 = ee.Number(image4_2.select('B11').reduceRegion(ee.Reducer.first(), point4, 5).get('B11')).getInfo()
        if b10_2 is None:
            text = colored(f'{name4} CSV failed at index {l}', "red", attrs=["reverse", "blink"])
            print(text)
            break
        b10L8_2 = ee.Number(image4_3.select('B10').reduceRegion(ee.Reducer.first(), point4, 5).get('B10')).getInfo()
        b11L8_2 = ee.Number(image4_3.select('B11').reduceRegion(ee.Reducer.first(), point4, 5).get('B11')).getInfo()
        RADIANCE_MULT_BAND_10 = image4_2.get('RADIANCE_MULT_BAND_10').getInfo()
        RADIANCE_MULT_BAND_11 = image4_2.get('RADIANCE_MULT_BAND_11').getInfo()
        RADIANCE_ADD_BAND_10 = image4_2.get('RADIANCE_ADD_BAND_10').getInfo()
        RADIANCE_ADD_BAND_11 = image4_2.get('RADIANCE_ADD_BAND_11').getInfo()
        b10_radiance = b10_2 * RADIANCE_MULT_BAND_10 + RADIANCE_ADD_BAND_10
        b11_radiance = b11_2 * RADIANCE_MULT_BAND_11 + RADIANCE_ADD_BAND_11
        RADIANCE_MULT_BAND_10L8 = image4_3.get('RADIANCE_MULT_BAND_10').getInfo()
        RADIANCE_MULT_BAND_11L8 = image4_3.get('RADIANCE_MULT_BAND_11').getInfo()
        RADIANCE_ADD_BAND_10L8 = image4_3.get('RADIANCE_ADD_BAND_10').getInfo()
        RADIANCE_ADD_BAND_11L8 = image4_3.get('RADIANCE_ADD_BAND_11').getInfo()
        b10_radianceL8 = b10L8_2 * RADIANCE_MULT_BAND_10L8 + RADIANCE_ADD_BAND_10L8
        b11_radianceL8 = b11L8_2 * RADIANCE_MULT_BAND_11L8 + RADIANCE_ADD_BAND_11L8
        date1 = (ee.Date(image4.get('system:time_start')).format('YYYY-MM-dd')).getInfo()
        date1L8 = (ee.Date(image4_3.get('system:time_start')).format('YYYY-MM-dd')).getInfo()
        surfTemp = ee.Number(image4.select("ST_B10").reduceRegion(ee.Reducer.first(), point4, 5).get("ST_B10")).getInfo() * scaleFactor + constant
        surfTemp8 = ee.Number(image4_8.select("ST_B10").reduceRegion(ee.Reducer.first(), point4, 5).get("ST_B10")).getInfo() * scaleFactor + constant
        productId = (image4.getString('LANDSAT_PRODUCT_ID')).getInfo()
        sceneId = (image4.getString('LANDSAT_SCENE_ID')).getInfo()
        productIdL8 = (image4_3.getString('LANDSAT_PRODUCT_ID')).getInfo()
        sceneIdL8 = (image4_3.getString('LANDSAT_SCENE_ID')).getInfo()
        list4.append([(-111.4302, 33.5396), date1, round(surfTemp, 3), round(b10_radiance, 3), round(b11_radiance, 3), productId, sceneId, date1L8, round(surfTemp8, 3), round(b10_radianceL8, 3), round(b11_radianceL8, 3), productIdL8, sceneIdL8])
        if l==c4Size-1:
            text = colored(name4 + " CSV saved", "green", attrs=["reverse", "blink"])
            print(text)

    with open(name4 + '.csv', 'w', newline='') as file:
        writer = csv.writer(file, delimiter=',')
        writer.writerows(list4)

#################################################################################

def function5():
    imageCollection5 = ee.ImageCollection("LANDSAT/LC09/C02/T1_L2") \
        .filterDate('2021-12-1', '2022-10-11') \
        .filterBounds(point5)
    imageList5 = imageCollection5.toList(imageCollection5.size())
    imageCollection5_8 = ee.ImageCollection("LANDSAT/LC08/C02/T1_L2") \
        .filterDate('2021-12-1', '2022-10-11') \
        .filterBounds(point5)
    imageList5_8 = imageCollection5_8.toList(imageCollection5_8.size())
    imageCollection5_2 = ee.ImageCollection("LANDSAT/LC09/C02/T1") \
        .filterDate('2021-12-1', '2022-10-11') \
        .filterBounds(point5)
    imageList5_2 = imageCollection5_2.toList(imageCollection5_2.size())
    imageCollection5_3 = ee.ImageCollection("LANDSAT/LC08/C02/T1") \
        .filterDate('2021-12-1', '2022-10-11') \
        .filterBounds(point5)
    imageList5_3 = imageCollection5_3.toList(imageCollection5_3.size())
    c5Size = min([imageCollection5_2.size().getInfo(), imageCollection5_3.size().getInfo(), imageCollection5.size().getInfo()])

    scaleFactor = 0.00341802
    constant = 149.0
    list5 = [["LongLat", "Date L9IM","L9ST [Kelvin]","L9B10 [radiance units]", "L9B11 [radiance units]", "L9 Product ID", "L9 Scene ID", "Date L8IM","L8ST [Kelvin]", "L8B10 [radiance units]", "L8B11 [radiance units]", "L8 Product ID", "L8 Scene ID"]]
    #print('Filtered Over Bartlett Reservoir: ', c5Size)
    print("Computing " + name5 + " Data...")

    for b in range(c5Size):
        image5 = ee.Image(imageList5.get(b))
        image5_8 = ee.Image(imageList5_8.get(b))
        image5_2 = ee.Image(imageList5_2.get(b))
        image5_3 = ee.Image(imageList5_3.get(b))
        b10_2 = ee.Number(image5_2.select('B10').reduceRegion(ee.Reducer.first(), point5, 5).get('B10')).getInfo()
        b11_2 = ee.Number(image5_2.select('B11').reduceRegion(ee.Reducer.first(), point5, 5).get('B11')).getInfo()
        b10L8_2 = ee.Number(image5_3.select('B10').reduceRegion(ee.Reducer.first(), point5, 5).get('B10')).getInfo()
        b11L8_2 = ee.Number(image5_3.select('B11').reduceRegion(ee.Reducer.first(), point5, 5).get('B11')).getInfo()
        if b10_2 is None:
            text = colored(f'{name5} CSV failed at index {b}', "red", attrs=["reverse", "blink"])
            print(text)
            break
        RADIANCE_MULT_BAND_10 = image5_2.get('RADIANCE_MULT_BAND_10').getInfo()
        RADIANCE_MULT_BAND_11 = image5_2.get('RADIANCE_MULT_BAND_11').getInfo()
        RADIANCE_ADD_BAND_10 = image5_2.get('RADIANCE_ADD_BAND_10').getInfo()
        RADIANCE_ADD_BAND_11 = image5_2.get('RADIANCE_ADD_BAND_11').getInfo()
        b10_radiance = b10_2 * RADIANCE_MULT_BAND_10 + RADIANCE_ADD_BAND_10
        b11_radiance = b11_2 * RADIANCE_MULT_BAND_11 + RADIANCE_ADD_BAND_11
        RADIANCE_MULT_BAND_10L8 = image5_3.get('RADIANCE_MULT_BAND_10').getInfo()
        RADIANCE_MULT_BAND_11L8 = image5_3.get('RADIANCE_MULT_BAND_11').getInfo()
        RADIANCE_ADD_BAND_10L8 = image5_3.get('RADIANCE_ADD_BAND_10').getInfo()
        RADIANCE_ADD_BAND_11L8 = image5_3.get('RADIANCE_ADD_BAND_11').getInfo()
        b10_radianceL8 = b10L8_2 * RADIANCE_MULT_BAND_10L8 + RADIANCE_ADD_BAND_10L8
        b11_radianceL8 = b11L8_2 * RADIANCE_MULT_BAND_11L8 + RADIANCE_ADD_BAND_11L8
        date1 = (ee.Date(image5.get('system:time_start')).format('YYYY-MM-dd')).getInfo()
        date1L8 = (ee.Date(image5_3.get('system:time_start')).format('YYYY-MM-dd')).getInfo()
        surfTemp = ee.Number(image5.select("ST_B10").reduceRegion(ee.Reducer.first(), point5, 5).get("ST_B10")).getInfo() * scaleFactor + constant
        surfTemp8 = ee.Number(image5_8.select("ST_B10").reduceRegion(ee.Reducer.first(), point5, 5).get("ST_B10")).getInfo() * scaleFactor + constant
        productId = (image5.getString('LANDSAT_PRODUCT_ID')).getInfo()
        sceneId = (image5.getString('LANDSAT_SCENE_ID')).getInfo()
        productIdL8 = (image5_3.getString('LANDSAT_PRODUCT_ID')).getInfo()
        sceneIdL8 = (image5_3.getString('LANDSAT_SCENE_ID')).getInfo()
        list5.append([(-111.6303, 33.8322), date1, round(surfTemp, 3), round(b10_radiance, 3), round(b11_radiance, 3), productId, sceneId, date1L8, round(surfTemp8, 3), round(b10_radianceL8, 3), round(b11_radianceL8, 3), productIdL8, sceneIdL8])
        if b==c5Size-1:
            text = colored(name5 + " CSV saved", "green", attrs=["reverse", "blink"])
            print(text)

    with open(name5 + '.csv', 'w', newline='') as file:
        writer = csv.writer(file, delimiter=',')
        writer.writerows(list5)

#################################################################################

def function6():
    imageCollection6 = ee.ImageCollection("LANDSAT/LC09/C02/T1_L2") \
        .filterDate('2021-12-1', '2022-10-11') \
        .filterBounds(point6)
    imageList6 = imageCollection6.toList(imageCollection6.size())
    imageCollection6_8 = ee.ImageCollection("LANDSAT/LC08/C02/T1_L2") \
        .filterDate('2021-12-1', '2022-10-11') \
        .filterBounds(point6)
    imageList6_8 = imageCollection6_8.toList(imageCollection6_8.size())
    imageCollection6_2 = ee.ImageCollection("LANDSAT/LC09/C02/T1") \
        .filterDate('2021-12-1', '2022-10-11') \
        .filterBounds(point6)
    imageList6_2 = imageCollection6_2.toList(imageCollection6_2.size())
    imageCollection6_3 = ee.ImageCollection("LANDSAT/LC08/C02/T1") \
        .filterDate('2021-12-1', '2022-10-11') \
        .filterBounds(point6)
    imageList6_3 = imageCollection6_3.toList(imageCollection6_3.size())
    c6Size = min([imageCollection6_2.size().getInfo(), imageCollection6_3.size().getInfo(), imageCollection6.size().getInfo()])

    scaleFactor = 0.00341802
    constant = 149.0
    list6 = [["LongLat", "Date L9IM","L9ST [Kelvin]","L9B10 [radiance units]", "L9B11 [radiance units]", "L9 Product ID", "L9 Scene ID", "Date L8IM","L8ST [Kelvin]", "L8B10 [radiance units]", "L8B11 [radiance units]", "L8 Product ID", "L8 Scene ID"]]
    #print('Filtered Over Bartlett Reservoir: ', c5Size)
    print("Computing " + name6 + " Data...")

    for c in range(c6Size):
        image6 = ee.Image(imageList6.get(c))
        image6_8 = ee.Image(imageList6_8.get(c))
        image6_2 = ee.Image(imageList6_2.get(c))
        image6_3 = ee.Image(imageList6_3.get(c))
        b10_2 = ee.Number(image6_2.select('B10').reduceRegion(ee.Reducer.first(), point6, 5).get('B10')).getInfo()
        b11_2 = ee.Number(image6_2.select('B11').reduceRegion(ee.Reducer.first(), point6, 5).get('B11')).getInfo()
        if b10_2 is None:
            text = colored(f'{name6} CSV failed at index {c}', "red", attrs=["reverse", "blink"])
            print(text)
            break
        b10L8_2 = ee.Number(image6_3.select('B10').reduceRegion(ee.Reducer.first(), point6, 5).get('B10')).getInfo()
        b11L8_2 = ee.Number(image6_3.select('B11').reduceRegion(ee.Reducer.first(), point6, 5).get('B11')).getInfo()
        RADIANCE_MULT_BAND_10 = image6_2.get('RADIANCE_MULT_BAND_10').getInfo()
        RADIANCE_MULT_BAND_11 = image6_2.get('RADIANCE_MULT_BAND_11').getInfo()
        RADIANCE_ADD_BAND_10 = image6_2.get('RADIANCE_ADD_BAND_10').getInfo()
        RADIANCE_ADD_BAND_11 = image6_2.get('RADIANCE_ADD_BAND_11').getInfo()
        b10_radiance = b10_2 * RADIANCE_MULT_BAND_10 + RADIANCE_ADD_BAND_10
        b11_radiance = b11_2 * RADIANCE_MULT_BAND_11 + RADIANCE_ADD_BAND_11
        RADIANCE_MULT_BAND_10L8 = image6_3.get('RADIANCE_MULT_BAND_10').getInfo()
        RADIANCE_MULT_BAND_11L8 = image6_3.get('RADIANCE_MULT_BAND_11').getInfo()
        RADIANCE_ADD_BAND_10L8 = image6_3.get('RADIANCE_ADD_BAND_10').getInfo()
        RADIANCE_ADD_BAND_11L8 = image6_3.get('RADIANCE_ADD_BAND_11').getInfo()
        b10_radianceL8 = b10L8_2 * RADIANCE_MULT_BAND_10L8 + RADIANCE_ADD_BAND_10L8
        b11_radianceL8 = b11L8_2 * RADIANCE_MULT_BAND_11L8 + RADIANCE_ADD_BAND_11L8
        date1 = (ee.Date(image6.get('system:time_start')).format('YYYY-MM-dd')).getInfo()
        date1L8 = (ee.Date(image6_3.get('system:time_start')).format('YYYY-MM-dd')).getInfo()
        surfTemp = ee.Number(image6.select("ST_B10").reduceRegion(ee.Reducer.first(), point6, 5).get("ST_B10")).getInfo() * scaleFactor + constant
        surfTemp8 = ee.Number(image6_8.select("ST_B10").reduceRegion(ee.Reducer.first(), point6, 5).get("ST_B10")).getInfo() * scaleFactor + constant
        productId = (image6.getString('LANDSAT_PRODUCT_ID')).getInfo()
        sceneId = (image6.getString('LANDSAT_SCENE_ID')).getInfo()
        productIdL8 = (image6_3.getString('LANDSAT_PRODUCT_ID')).getInfo()
        sceneIdL8 = (image6_3.getString('LANDSAT_SCENE_ID')).getInfo()
        list6.append([(-111.6303, 33.8322), date1, round(surfTemp, 3), round(b10_radiance, 3), round(b11_radiance, 3), productId, sceneId, date1L8, round(surfTemp8, 3), round(b10_radianceL8, 3), round(b11_radianceL8, 3), productIdL8, sceneIdL8])
        if c==c6Size-1:
            text = colored(name6 + " CSV saved", "green", attrs=["reverse", "blink"])
            print(text)

    with open(name6 + '.csv', 'w', newline='') as file:
        writer = csv.writer(file, delimiter=',')
        writer.writerows(list6)


if __name__ == "__main__":
    startTime = time.time()

    p1 = Process(target=function1)
    p1.start()
    p2 = Process(target=function2)
    p2.start()
    p3 = Process(target=function3)
    p3.start()
    p4 = Process(target=function4)
    p4.start()
    p5 = Process(target=function5)
    p5.start()
    #p6 = Process(target=function6)
    #p6.start()
    p1.join()
    p2.join()
    p3.join()
    p4.join()
    p5.join()
    #p6.join()


    executionTime = (time.time() - startTime)
    min = math.floor(executionTime / 60)
    seconds = math.floor(executionTime - (min * 60))
    print(f'Execution time: {min}min {seconds}s ')
