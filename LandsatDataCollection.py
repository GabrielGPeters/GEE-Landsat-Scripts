# Imports
import ee
import csv
from termcolor import colored
import time
import math

# initializing the library
ee.Initialize()

'''
    author::        
        Gabriel Peters, ugrad (ggp2366@rit.edu)
    copyright::     
        Copyright (C) 2022, Rochester Institute of Technology
    version::       
        2.0.1
    purpose::
        1. This code is designed to provide estimated surface temperature data
           from Landsat 8/9 Level 2 images, Band 11 and Band 10 radiance data from 
           Landsat 8/9 Collection 2 Level 1 images, for a specific set of input coordinates
        2. Data is written into a CSV file
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

'''

name = input("Enter location name: ")
lat = float(input("Enter latitude: "))
long = float(input("Enter longitude: "))
loc = ee.Geometry.Point([long, lat])
datayn = input("Select output data? (y|n)(n outputs all data): ")

if (datayn == "y"):
    check = True
    infoyn = input("Image info? (y|n): ")
    if (infoyn == "y"):
        info = True
    if (infoyn == "n"):
        info = False
    L9yn = input("Landsat 9 data? (y|n): ")
    if (L9yn == "y"):
        L9 = True
    if (L9yn == "n"):
        L9 = False
    L8yn = input("Landsat 8 data? (y|n): ")
    if (L8yn == "y"):
        L8 = True
    if (L8yn == "n"):
        L8 = False
    if (L9yn == "n" and L8yn == "n"):
        endtext = colored("ERROR: no data requested", "red", attrs=["reverse", "blink"])
        print(endtext)
        quit()

if (datayn == "n"):
    check = False

# start clock
startTime = time.time()

# L9 ST data
imageCollectionL9C2L2 = ee.ImageCollection("LANDSAT/LC09/C02/T1_L2") \
    .filterDate('2021-12-1', '2022-10-11') \
    .filterBounds(loc)
imageListL9C2L2 = imageCollectionL9C2L2.toList(imageCollectionL9C2L2.size())

# L8 ST data
imageCollectionL8C2L2 = ee.ImageCollection("LANDSAT/LC08/C02/T1_L2") \
    .filterDate('2021-12-1', '2022-10-11') \
    .filterBounds(loc)
imageListL8C2L2 = imageCollectionL8C2L2.toList(imageCollectionL8C2L2.size())

# L9 B10/B11 radiance data
imageCollectionL9C2T1 = ee.ImageCollection("LANDSAT/LC09/C02/T1") \
    .filterDate('2021-12-1', '2022-10-11') \
    .filterBounds(loc)
imageListL9C2T1 = imageCollectionL9C2T1.toList(imageCollectionL9C2T1.size())

# L8 B10/B11 radiance data
imageCollectionL8C2T1 = ee.ImageCollection("LANDSAT/LC08/C02/T1") \
    .filterDate('2021-12-1', '2022-10-11') \
    .filterBounds(loc)
imageListL8C2T1 = imageCollectionL8C2T1.toList(imageCollectionL8C2T1.size())

size = min([imageCollectionL9C2T1.size().getInfo(), imageCollectionL8C2T1.size().getInfo(), imageCollectionL9C2T1.size().getInfo()])

scaleFactor = 0.00341802
constant = 149.0

if (check == True):
    if(info == True):
        if(L9 == True and L8 == True):
            list = [["LongLat", "Date L9IM", "L9ST [Kelvin]", "L9B10 [radiance units]", "L9B11 [radiance units]",
                    "L9 Product ID", "L9 Scene ID",
                    "Date L8IM", "L8ST [Kelvin]", "L8B10 [radiance units]",
                    "L8B11 [radiance units]", "L8 Product ID", "L8 Scene ID"]]
        if(L9 == True and L8 == False):
            list = [["LongLat", "Date L9IM", "L9ST [Kelvin]", "L9B10 [radiance units]", "L9B11 [radiance units]",
                    "L9 Product ID", "L9 Scene ID"]]
        if(L9 == False and L8 == True):
            list = [["LongLat", "Date L8IM", "L8ST [Kelvin]", "L8B10 [radiance units]", "L8B11 [radiance units]",
                    "L8 Product ID", "L8 Scene ID"]]
        if(L9 == False and L8 == False):
            endtext = colored("ERROR: selected no data", "red", attrs=["reverse", "blink"])
            print(endtext)
            quit()
    if(info == False):
        if(L9 == True and L8 == True):
            list = [["L9ST [Kelvin]", "L9B10 [radiance units]", "L9B11 [radiance units]",
                     "L8ST [Kelvin]", "L8B10 [radiance units]", "L8B11 [radiance units]"]]
        if(L9 == True and L8 == False):
            list = [["L9ST [Kelvin]", "L9B10 [radiance units]", "L9B11 [radiance units]"]]
        if(L9 == False and L8 == True):
            list = [["L8ST [Kelvin]", "L8B10 [radiance units]", "L8B11 [radiance units]"]]

if (check == False) :
    L9 == True
    L8 == True
    info == True
    list = [["LongLat", "Date L9IM","L9ST [Kelvin]","L9B10 [radiance units]", "L9B11 [radiance units]", "L9 Product ID", "L9 Scene ID", "Date L8IM","L8ST [Kelvin]", "L8B10 [radiance units]", "L8B11 [radiance units]", "L8 Product ID", "L8 Scene ID"]]

#print('Filtered Over ' + name +': ', c1Size)
print("Computing " + name + " Data...")

for i in range(size):
    # getting image for each collection
    imageL9C2L2 = ee.Image(imageListL9C2L2.get(i))
    imageL8C2L2 = ee.Image(imageListL8C2L2.get(i))
    imageL9C2T1 = ee.Image(imageListL9C2T1.get(i))
    imageL8C2T1 = ee.Image(imageListL8C2T1.get(i))

    if(L9 == True):
        b10L9 = ee.Number(imageL9C2T1.select('B10').reduceRegion(ee.Reducer.first(), loc, 5).get('B10')).getInfo()
        b11L9 = ee.Number(imageL9C2T1.select('B11').reduceRegion(ee.Reducer.first(), loc, 5).get('B11')).getInfo()
        if b10L9 is None:
            text = colored(f'{name} CSV failed at index {i}', "red", attrs=["reverse", "blink"])
            print(text)
            break
        RADIANCE_MULT_BAND_10L9 = imageL9C2T1.get('RADIANCE_MULT_BAND_10').getInfo()
        RADIANCE_MULT_BAND_11L9 = imageL9C2T1.get('RADIANCE_MULT_BAND_11').getInfo()
        RADIANCE_ADD_BAND_10L9 = imageL9C2T1.get('RADIANCE_ADD_BAND_10').getInfo()
        RADIANCE_ADD_BAND_11L9 = imageL9C2T1.get('RADIANCE_ADD_BAND_11').getInfo()
        b10_radianceL9 = b10L9 * RADIANCE_MULT_BAND_10L9 + RADIANCE_ADD_BAND_10L9
        b11_radianceL9 = b11L9 * RADIANCE_MULT_BAND_11L9 + RADIANCE_ADD_BAND_11L9
        surfTempL9 = ee.Number(imageL9C2L2.select("ST_B10").reduceRegion(ee.Reducer.first(), loc, 5).get("ST_B10")).getInfo() * scaleFactor + constant
        dateL9 = (ee.Date(imageL9C2L2.get('system:time_start')).format('YYYY-MM-dd')).getInfo()
        productIdL9 = (imageL9C2L2.getString('LANDSAT_PRODUCT_ID')).getInfo()
        sceneIdL9 = (imageL9C2L2.getString('LANDSAT_SCENE_ID')).getInfo()
    if (L8 == True):
        b10L8 = ee.Number(imageL8C2T1.select('B10').reduceRegion(ee.Reducer.first(), loc, 5).get('B10')).getInfo()
        b11L8 = ee.Number(imageL8C2T1.select('B11').reduceRegion(ee.Reducer.first(), loc, 5).get('B11')).getInfo()
        if b10L8 is None:
            text = colored(f'{name} CSV failed at index {i}', "red", attrs=["reverse", "blink"])
            print(text)
            break
        RADIANCE_MULT_BAND_10L8 = imageL8C2T1.get('RADIANCE_MULT_BAND_10').getInfo()
        RADIANCE_MULT_BAND_11L8 = imageL8C2T1.get('RADIANCE_MULT_BAND_11').getInfo()
        RADIANCE_ADD_BAND_10L8 = imageL8C2T1.get('RADIANCE_ADD_BAND_10').getInfo()
        RADIANCE_ADD_BAND_11L8 = imageL8C2T1.get('RADIANCE_ADD_BAND_11').getInfo()
        b10_radianceL8 = b10L8 * RADIANCE_MULT_BAND_10L8 + RADIANCE_ADD_BAND_10L8
        b11_radianceL8 = b11L8 * RADIANCE_MULT_BAND_11L8 + RADIANCE_ADD_BAND_11L8
        surfTempL8 = ee.Number(imageL8C2L2.select("ST_B10").reduceRegion(ee.Reducer.first(), loc, 5).get("ST_B10")).getInfo() * scaleFactor + constant
        dateL8 = (ee.Date(imageL8C2T1.get('system:time_start')).format('YYYY-MM-dd')).getInfo()
        productIdL8 = (imageL8C2T1.getString('LANDSAT_PRODUCT_ID')).getInfo()
        sceneIdL8 = (imageL8C2T1.getString('LANDSAT_SCENE_ID')).getInfo()
    if (check == False):
        list.append([(lat, long), dateL9, round(surfTempL9, 3), round(b10_radianceL9, 3), round(b11_radianceL9, 3), productIdL9, sceneIdL9, dateL8, round(surfTempL8, 3), round(b10_radianceL8, 3), round(b11_radianceL8, 3), productIdL8, sceneIdL8])
    if (check == True):
        if(info == True):
            if(L9 == True and L8 == True):
                list.append([(lat, long), dateL9, round(surfTempL9, 3), round(b10_radianceL9, 3), round(b11_radianceL9, 3),
                            productIdL9, sceneIdL9, dateL8, round(surfTempL8, 3), round(b10_radianceL8, 3),
                            round(b11_radianceL8, 3), productIdL8, sceneIdL8])
            if(L9 == True and L8 == False):
                list.append([(lat, long), dateL9, round(surfTempL9, 3), round(b10_radianceL9, 3), round(b11_radianceL9, 3),
                            productIdL9, sceneIdL9])
            if(L9 == False and L8 == True):
                list.append([(lat, long), dateL8, round(surfTempL8, 3), round(b10_radianceL8, 3), round(b11_radianceL8, 3),
                            productIdL8, sceneIdL8])
        if (info == False):
            if (L9 == True and L8 == True):
                list.append([round(surfTempL9, 3), round(b10_radianceL9, 3), round(b11_radianceL9, 3),
                             round(surfTempL8, 3), round(b10_radianceL8, 3), round(b11_radianceL8, 3)])
            if (L9 == True and L8 == False):
                list.append(
                    [round(surfTempL9, 3), round(b10_radianceL9, 3), round(b11_radianceL9, 3)])
            if (L9 == False and L8 == True):
                list.append(
                    [round(surfTempL8, 3), round(b10_radianceL8, 3), round(b11_radianceL8, 3)])
    if i==size-1:
        text = colored(name + " CSV saved", "green", attrs=["reverse", "blink"])
        print(text)

with open(name + '.csv', 'w', newline='') as file:
    writer = csv.writer(file, delimiter=',')
    writer.writerows(list)


executionTime = (time.time() - startTime)
min = math.floor(executionTime / 60)
seconds = math.floor(executionTime - (min * 60))
print(f'Execution time: {min}min {seconds}s ')
