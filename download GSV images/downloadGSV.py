# downloadGSV.py #
# Author: Andrew Larkin
# Developed for Perry Hystad, Oregon State University
# Date last modified: March 4, 2016
# Script for downloading Google Street View panorama images at a given latitutde/longitude coordinate pair
# Panorama images are downloaded and tiles and then mosaicked to create the complete image

########## import libraries #########
import urllib
import os
import sys
from PIL import Image
import csv

########### define filepaths and constants #########
countyNumber = "53059"  # for folder organization purposes
folder = os.path.dirname(sys.argv[0]) + "/"
countyFolder = folder + "panoramaImages/County" + countyNumber + "/"
metaData = folder + "GoogleImageMetaData/textFolder/C" + countyNumber + ".txt"
outputCSV = folder + "GoogleImageMetaData/csvFolder/C" + countyNumber + ".csv"
compositeFolder = folder + "panoramaImages/allComposites/"
heightSize = 13 # number of tiles in each row
widthSize = 26 # number of tiles in each column 




########## helper functions ##########




# download a series of images based on a unique id
# INPUTS:
#    panIds (string array) - array of unique ids, with one id for each panorama image to download
def downloadBatchPanoramas(panIds):
    for panId in panIds:
        if not (os.path.exists(compositeFolder + "p" + panId + ".jpg" )):
            try:
                downloadPanorama(panId,countyFolder)
            except Exception as e:
                print("couldn't download panID " + panId)


# download a single panorama images
# INPUTS:
#    panId (string) - unique id for the panorama image to donwload
#    countyFolder (string) - filepath to the folder where the panorama image should be saved
def downloadPanorama(panId,countyFolder):
    folderToCreate = countyFolder + "p" + panId
    blank_image = Image.new("RGB", (512*widthSize, 512*heightSize))
    if not(os.path.isdir(folderToCreate)):
        os.makedirs(folderToCreate)
        
    # download one tile at a time, in row-major order.  Mosaic the tiles as you go
    for colNumber in range(0,widthSize):
        for rowNumber in range(0,heightSize):
            url = "http://cbk0.google.com/cbk?output=tile&panoid=" + panId + "&zoom=5&x=" + str(colNumber) + "&y=" + str(rowNumber)
            outputFile = folderToCreate + "/col" + str(colNumber) + "row" + str(rowNumber) + ".jpg"
            urllib.urlretrieve(url, outputFile)
            im = Image.open(outputFile)
            colLocation = colNumber*512
            rowLocation = rowNumber*512
            f2 = Image.open(outputFile)
            blank_image.paste(im, (colLocation, rowLocation))
    # save the mosaiced tiles to the output folder with the name based on panId
    blank_image.save(compositeFolder + "p" + panId + ".jpg" )



# load data from text file into array format
# INPUTS:
#    inputFile (string) - filepath to text file 
def processPanoramaInfo(inputFile):
    csvArray = [[],[],[],[]]
    file = open(inputFile) # open inthe input file and move past the 6 lines of headers     
    a = file.readline()
    startIndex = 1
    while(a):
        a = a.replace(" ", "")
        a = a.replace("(","")
        a = a.replace(")","")
        if(len(a) > 26):
            startIndex = 1
            columnNumber = 0
            while(startIndex > 0):
                if(columnNumber==0):
                    startIndex = 0
                endIndex = a.find(',',startIndex)
                csvArray[columnNumber].append(a[startIndex:endIndex])
                startIndex = endIndex + 1
                columnNumber +=1
        a = file.readline()
    print("completed processPanoramaInfo")
    return(csvArray)
        

# write data in an array to a csv file
# INPUTS:
#   csvArray (string) - data to be written
#   tempFileName (string) - name, including full filepath, of csv file to write
def writeCSVArray(csvArray,tempFileName):
    a = open(tempFileName, 'wb')
    columnIndex = 0
    rowIndex = 0
    a.write("panId, panDate, panLat, panLong \n")
    while rowIndex < (len(csvArray[0])-10):
        while columnIndex < len(csvArray):
            a.write(str(csvArray[columnIndex][rowIndex]))
            a.write(",")
            columnIndex+=1
        columnIndex = 0
        rowIndex+=1
        a.write("\n")   
    a.close()
    return(tempFileName)

# read data from csv file 
# INPUTS:
#   inputCSV (string) - filepath including name of the csv file to read
def readPanCSV(inputCSV):
    csvArray = []
    with open(inputCSV) as f: # open inthe input file and move past the 6 lines of headers     
        reader = csv.DictReader(f, dialect=f) # identify the names of the columns (i.e. variables) in the csv file
        for row in reader: # read a row as {column1: value1, column2: value2,...}
            for (k,v) in row.items(): # go over each column name and value 
                if(k == "panId"): # if the variable name is in the list of variables in linkWebDict (variables we want to keep)
                    csvArray.append(v)
        del reader, row
        return(csvArray)       
    print("completed reading CSV")

############ main function #########

def main():
    csvArray = processPanoramaInfo(metaData,countyFolder)
    writeCSVArray(csvArray,outputCSV)
    panIds = readPanCSV(outputCSV)
    downloadBatchPanoramas(panIds)
    print("completed main function")
    

### end of downloadGSV.py ###