INTRODUCTION

This repository contains a collection of Javascript code I wrote for use in Google Earth Engine for satellite sensor characterization and research.

1. L9-8Band1Comparison
    - Compares band 1 data from Landsat 8 and 9 imagery since December 2021 to determine issues in Landsat 9 calibration.

2. L9StripeCharacterization
    - Filters L9 image collections to clear images taken in a 24 hour period 2 days ago over water, and selects the first image.
      Exports bands 10 and 11 of the image as well as the percent difference between the two, revealing stripe artifacts as a result 
      of faulty sensor calibration

3. PondSurfaceTemperatures
    - Gathers L9 L2 B10 surface temperature estimates at buoy locations in Sandy Pond, NY to compare to on-site surface temperature data for 
      the purpose of determining how accurate the satellite data is 

NOTE:   Each code has a list of imports underneath the comment "IMPORTS". If you import those it should clean up the code and go into the top of the script, especially do this for "L9StripeCharacterization"
