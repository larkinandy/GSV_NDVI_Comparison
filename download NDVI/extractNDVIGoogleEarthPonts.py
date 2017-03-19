# extractNDVIGoolgeEarthPoints.py
# Author: Andy Larkin
# Created for Perry Hystad, Oregon State University
# Date created: March 2016.
# Download Landsat 5 NDVI estimates from Google Earth Engine.  # Estimates are screened for cloud cover,
# and water bodies.  Note that accessing data from the Google Earth Engine requires an authorization 
# cookie not included in this file.


##### import requied modules ######
import ee
import time
import datetime
import csv
import math
import os
import sys
ee.Initialize()


####### variables user might want to change ############
DisplayGUI = False
folder = os.path.dirname(sys.argv[0]) + "/"
datesCSVFolder = folder + "csvByDate/"
outputFolder = folder + "GEE_NDVI/Landsat5/"
bufferDistance = 50;
BATCH_SIZE = 100
VARIABLE_NAME = "NDVI_Landsat"
#startDate = '2000-02-01'
#endDate = '2001-12-31'
collectionName = 'LANDSAT/LC8_L1T_32DAY_NDVI'  #'LANDSAT/LT5_L1T_32DAY_NDVI'
tempCSVFolder = folder + "tempCSVs/"
CSV_DICT = ["panLat","panLong","pandDate","panID"]
NEW_LINE = "\n"
tempImage = ee.Image()




################ helper functions ##############




# load data from the csv containing lat/long coordinates, date, and unique Id for points of interest
# INPUTS:
#    inputFile (string) - compelete filepath 
# OUTPUTS:
#    csvArray (array of arrays) - an array of arrays containing csv data
def readCSVFile(inputFile):
    csvArray = [[],[]]
    with open(inputFile) as f: # open inthe input file and move past the 6 lines of headers     
        reader = csv.DictReader(f, dialect=f) # identify the names of the columns (i.e. variables) in the csv file
        for row in reader: # read a row as {column1: value1, column2: value2,...}
            for (k,v) in row.items(): # go over each column name and value 
                if(k in CSV_DICT): # if the variable name is in the list of variables in linkWebDict (variables we want to keep)
                    csvArray[CSV_DICT.index(k)].append(float(v))
        del reader, row
    print("completed importing csv file")
    return(csvArray)     



# create geom objects from lat/long coordinates
# INPUTS:
#    csvArray (array of arrays) - array containing lat/long coords
# OUTPUTS:
#    featureList (Geometry Feature) - unique GEE object containing a feature list of geometry objects
def makeGeomPoints(csvArray):
    i = 0
    featureList = []
    while i < len(csvArray[1]):
        featureList.append(ee.Feature(ee.Geometry.Point(csvArray[1][i],csvArray[0][i])))
        i+=1
    print ("completed creating geometric points")
    return(featureList)


# filter NDVI images to the range covered by the extraction points
def filterCatalogSet():  
    collection = ee.ImageCollection(collectionName)
    datedCollect = collection.filterDate(startDate,endDate)
    return(datedCollect)


# extrract NDVI at one geom point
# INPUTS:
#    inputVals (geom point) - GEE object of a single point
# OUTPUTS:
#    inputVals2 (geom point) - GEE object with NDVI value added to the point
def bufferRunMap(inputVals):
    filteredCatalog = filterCatalogSet()
    catalogDates = filteredCatalog.toList(10000)
    timeStart = band.get('system:time_start')
    projString = 'PROJCS["North_America_Equidistant_Conic",GEOGCS["GCS_North_American_1983",DATUM["D_North_American_1983",SPHEROID["GRS_1980",6378137,298.257222101]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Equidistant_Conic"],PARAMETER["False_Easting",0],PARAMETER["False_Northing",0],PARAMETER["Central_Meridian",-96],PARAMETER["Standard_Parallel_1",20],PARAMETER["Standard_Parallel_2",60],PARAMETER["Latitude_Of_Origin",40],UNIT["Meter",1]]'
    proj = ee.Projection(projString)    
    a = band.reduceRegion(ee.Reducer.mean(),inputVals.geometry(),5,proj)
    inputVals2 = inputVals.set({str(timeStart.getInfo()):a})
    return(inputVals2)
  
  
  
# extract NDVI values from all geom points within a specific time range
# INPUTS:
#    inputPointDataset (Feature Collection) - GEE object, similar to a shapefile of points
#    inputRasterDataset (Image Collection) - GEe object, similar to a raster catalog
#    numRasters (GEE Number) - GEE representation of a number
# OUTPUTS:
#    currentDataset (Feature Collection) - inputPointDataset with NDVI values appended
def extractNDVIValues(inputPointDataset,inputRasterDataset,numRasters):
    print("extracting NDVI values from satellite imagery...")
    currentDataset = inputPointDataset
    for rasterNum in range(0,numRasters.getInfo()):
        try:
            if((rasterNum%2) ==0):
                time.sleep(0.25)
            tempImage = ee.Image(inputRasterDataset.get(rasterNum))
            if(rasterNum==0):
                currentDataset = inputPointDataset
            global band
            band = tempImage.select('NDVI')
            currentDataset = currentDataset.map(lambda f: bufferRunMap(f))
            del band    
        except:
            currentDataset = inputPointDataset
        print("completed " + str(rasterNum) + " out of " + str(numRasters.getInfo()) + " rasters")
    print("completed extracting NDVI values")
    return(currentDataset)



# create buffers from points
# INPUTS:
#    inputPoints (Feature Collection) - collection of points
# OUTPUTS:
#    bufferedCollect (Feature Collection) - collection of buffers around input dataset points
def bufferPointData(inputPoints):
    tempCollection = ee.FeatureCollection(inputPoints)
    bufferedCollect = tempCollection.map(lambda f: f.buffer(bufferDistance))    
    return(bufferedCollect)


# read data from CSV and load into GEE format
# INPUTS:
#    inputCSV (string) - exact filepath to csv file
# OUTPUTS:
#    residPoints (Feature Collection) - collection of points in GEE format
#    csvArray (array array) - csv data stored in array format
def importCSVData(inputCSV):
    csvArray = readCSVFile(inputCSV)
    residPoints = makeGeomPoints(csvArray)    
    return([residPoints,csvArray])


# create a GEE image catalog object, and filter the date and spatial extent
# OUTPUTS:
#    catalogDates (GEE List) - GEE object of a list of catalog dates
#    numRaster (GEE number) - GEE object of the number of rasters that cover
#                             the date and spatial range of interest
def setupRasterData():
    filteredCatalog = filterCatalogSet()
    catalogDates = filteredCatalog.toList(10000)
    numRasters = ee.Number(filteredCatalog.size())    
    return([catalogDates,numRasters])


# extract NDVI from all points
# INPUTS:
#    pointObject (Feature Collection) - collection of point objects in GEE format
# OUTPUTS:
#    valList (float array) - epoch time of values extracted from NDVI rasters
#    pointStrings (string array) - points of interest with NDVI values in string format
def extractDataFromPoints(pointObject):
    listVersion = pointObject.toList(100000)
    valList = []
    pointStrings = []
    pointsLeft = True
    index = 0
    while(pointsLeft == True):
        try:
            b = ee.Feature(listVersion.get(index))
            testString = str(b.getInfo())
            endString = False
            startVal = 0
            subsetString = testString[testString.find('properties'):len(testString)]
            pointString = ""
            valList = []
            while(endString == False):
                startVal = subsetString.find('u',startVal)
                endVal = subsetString.find(':',startVal+1)-1
                timeStamp = subsetString[startVal+2:endVal]
                startVal = subsetString.find(':',endVal + 2)
                endVal = subsetString.find('},',startVal)
                NDVI = subsetString[startVal+2:endVal]
                startVal = endVal + 1
                if(endVal == -1):   
                    NDVI = NDVI.strip('}')
                    endString = True
                valList.append(timeStamp)
                pointString = pointString + str(NDVI) + "," 
            pointString = pointString[0:len(pointString)-1]
            pointStrings.append(pointString + " \n")
        except Exception as E:
            print("completed extracting data from geopoints")
            pointsLeft = False
        index+=1
    print("completed extracting values from geom points")
    return([valList,pointStrings])
        
    
# convert header dates from epoch into Julian format, and write as a header for a csv file
# INPUTS:
#    csvHeaderVals (string array) - array of sampled time points, in epoch format
# OUTPUTS:
#    timeString (string) - string containing dates as a header for a csv file
def getHeaderDates(csvHeaderVals):
    timeString = ""
    for epochTime in csvHeaderVals:    
        timeString = timeString + time.strftime('%Y%j', time.localtime(int(epochTime)/1000)) + ','
    timeString = timeString[0:len(timeString)-1]
    print("completed converting raster dates from epoch to Julian format")
    return(timeString)


# write a temporary csv file for a subset of the spatial points of interest
# INPUTS:
#    CSVHeader (string) - header for the csv file to write
#    rowVals (float array) - values to write in the csv file
#    batchNumber (int) - index number for the subset of the total spatial point dataset
def writeTempCSV(CSVHeader,rowVals,batchNumer):
    i = 0
    tempFilename =tempCSVFolder + "tempCSVsBatch" + str(batchNumer) + ".csv"
    a = open(tempFilename, 'wb')
    a.write(CSVHeader)
    a.write(" \n ")
    for singleRow in rowVals:
        a.write(singleRow)
    a.close()
    
    
    
# merge temporary CSV files into an array containing all of the CSV data
# INPUTS:
#    inputCSVFolder (string) - filepath to the folder containing temporary CSV files
# OUTPUTS
#    csv Array (array array) - object containing merged CSV data
def mergeCSVFiles(inputCSVFolder):
    fileList = os.listdir(inputCSVFolder)
    tempDict = []
    firstFile = True
    # for each temporary CSV file
    for fileName in fileList:
        if(fileName[len(fileName)-3:len(fileName)]=='csv'):
            with open(inputCSVFolder + fileName) as f: # open inthe input file and move past the 6 lines of headers     
                reader = csv.DictReader(f, dialect=f) # identify the names of the columns (i.e. variables) in the csv file
                for row in reader: # read a row as {column1: value1, column2: value2,...}
                    if(firstFile == True):
                        csvArray = []
                        firstFile=False
                        for (k,v) in row.items(): # go over each column name and value 
                            if(k not in tempDict):
                                tempDict.append(k)
                                tempArray = [k]
                                csvArray.append(tempArray)
                        
                    for (k,v) in row.items():
                        csvArray[tempDict.index(k)].append(v)
                del reader, row
            print("completed importing csv file")
    return(csvArray)     




# write data into a single final output CSV file
# INPUTS:
#    NDVIArray (float array) - array containing NDVI values
#    latLongArray (array array) - two arrays containing lat and long values
#    outputFile (string) - name and filepath to the csv file that will be written
def writeOutputArray(NDVIArray, latLongArray,outputFile):
    a = open(outputFile, 'wb')
    a.write("latitude,longitude,")
    a.write(VARIABLE_NAME )
    a.write(" \n ")
    for i in range(1,len(NDVIArray[0])):
        a.write(str(latLongArray[0][i-1]))
        a.write(",")
        a.write(str(latLongArray[1][i-1]))
        a.write(",")
        if(len(NDVIArray) == 2):
            avgNDVI = str((float(NDVIArray[0][i]) + float(NDVIArray[1][i]))/2.0)
        else:
            avgNDVI = NDVIArray[0][i]
        a.write(avgNDVI)
        a.write(' \n ')
    a.close()    
        
        
        
############ main function ########


def main():
    # get the list of input data.  For each input data file, extract data
    fileNames = os.listdir(datesCSVFolder)
    for fileName in fileNames:
        try:
            csvFile = datesCSVFolder + fileName
            outputFile = outputFolder + csvFile[len(csvFile)-11:len(csvFile)-4] + ".csv"
            if not os.path.exists(outputFile):
                # filter NDVI catalog by date range covered by input data
                global startDate
                startDate = csvFile[len(csvFile)-11:len(csvFile)-4] + "-01"
                global endDate
                endDate = csvFile[len(csvFile)-11:len(csvFile)-4] + "-30"      
                [entireCSVData,latLongArray] = importCSVData(csvFile)
                [catalogDates,numRasters] = setupRasterData()
                numBatches = int(math.ceil(len(entireCSVData)/float(BATCH_SIZE)))
                # for eaach subset of data, extract NDVI values 
                for i in range(0,numBatches):
                    batchSample = entireCSVData[(i*BATCH_SIZE):((i+1)*BATCH_SIZE)]
                    bufferedPoints = bufferPointData(batchSample)
                    extractedPoints = extractNDVIValues(bufferedPoints,catalogDates,numRasters)
                    [headerVals,pointStrings] = extractDataFromPoints(extractedPoints)
                    headerTimeString = getHeaderDates(headerVals)
                    writeTempCSV(headerTimeString,pointStrings,i)
                # merge subset of data and write to output array
                NDVIArray = mergeCSVFiles(tempCSVFolder)
                writeOutputArray(NDVIArray,latLongArray, outputFile)
                for fileName in os.listdir(tempCSVFolder):
                    os.remove(tempCSVFolder + fileName)
        except Exception as e:
            print str(e)
    print("the end")
main()



### end of extractNDVIGoogleEarthEngine.py ###