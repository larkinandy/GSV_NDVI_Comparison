# create_GSV_webscript.py
# Author: Andy Larkin
# Created for Perry Hystad, Oregon State University
# Date created: 3/2/2016
# this script modifies html source code to extract panorama ids of Google Street images at specified lat/long coordinates


########## import modules ######
import csv
import glob
import os
import sys
import random


######## define constants ##########
pathname = os.path.dirname(sys.argv[0]) + "/"
topCSVFile = pathname + "get_PanID_Bottom_Half.txt"
bottomCSVFile = pathname + "get_PanID_Bottom_Half.txt"
tempFilename = pathname + "tempfile.txt"
csvFile = pathname + "PortlandRoadFiles/csvFiles/tl_2015_53059_roads.csv"
outputFile = pathname + "PortlandRoadFiles/completedWebScripts/county_53059.txt"
CSV_DICT = ["latitude","longitude"]
defaultConstants = False



############## helper functions ############




# read an input csv file and store as an array of arrays
# INPUTS:
#    inputFile (string) - full filepath of csv file to read
# OUTPUTS:
#    csvArray (array) - an array of arrays, containing the csv data
def readCSVFile(inputFile):
    csvArray = [[],[]]
    with open(inputFile) as f: # open inthe input file and move past the 6 lines of headers     
        reader = csv.DictReader(f, dialect=f) # identify the names of the columns (i.e. variables) in the csv file
        for row in reader: # read a row as {column1: value1, column2: value2,...}
            for (k,v) in row.items(): # go over each column name and value 
                if(k in CSV_DICT): # if the variable name is in the list of variables in linkWebDict (variables we want to keep)
                    csvArray[CSV_DICT.index(k)].append(float(v))
        del reader, row
        return(csvArray)     


# write latitude/longitude coordinates into the appropriate div in the html file
# INPUTS:
#   csvArray (array) - an array of latitude/longitude arrays
# OUTPUTS:
#   tempFilename (string) - filepath to file containing the html code, modified
#                           to inclulde the lat/long coordinates
def makeGeomPoints(csvArray):
    a = open(tempFilename, 'wb')
    a.write("var latitude = [")
    index = 0
    while index < len(csvArray[1]):
        a.write(str(csvArray[0][index]))
        if(index<len(csvArray[1])-1):
            a.write(',')
        index+=1
    a.write('];')
    a.write("\n")
    a.write("var longitude = [")
    index = 0
    while index < len(csvArray[1]):
        a.write(str(csvArray[1][index]))
        if(index<len(csvArray[1])-1):
            a.write(',')
        index+=1
    a.write('];')
    a.write("\n")    
    a.close()
    return(tempFilename)
    
    
# merge multiple text files, each with a piece of the overall html code, to create a 
# final complete html document
# INPUTS:
#    fileList (string array) - array of filenames, including the filepath
#    outputFile (string) - name of the html file that's written, including filepath
def combineTextFiles(fileList,outputFile):
    with open (outputFile, "wb") as outfile:
        for f in fileList:
            with open(f,"rb") as infile:
                outfile.write(infile.read())
                outfile.write("\n")
    
    
# screen a list of candidate latitude/longitude coordinate pairs and remove duplicates
# this is the second step in the random selection process to ensure random selection
# without replacement
# INPUTS:
#    inputValueList (array) - array of latitude and longitude arrays
# OUTPUTS:
#    uniqueVals (array) - same as the input array, but with removed duplicates
def getUniqueValues(inputValueList):
    latitSequence = inputValueList[0]
    longitSequence = inputValueList[1]
    uniqueLatit = []
    uniqueLongit = []
    [uniqueLatit.append(item) for item in latitSequence if item not in uniqueLatit]
    [uniqueLongit.append(item) for item in longitSequence if item not in uniqueLongit]
    uniqueVals = [uniqueLatit,uniqueLongit]
    return(uniqueVals)
    
    
# randomlySelect indeces in a csv array
# INPUTS:
#   csvArray (array) - an array of latitutde/longitude arrays
# OUTPUTS:
#   randArray (array) - a random selection of the input array
def randomlySelect(csvArray):
    randArray = [[],[]]
    for numSelect in range(0,870):
        randNum = random.randint(0,len(csvArray[1])-1)
        randArray[0].append(csvArray[0][randNum])
        randArray[1].append(csvArray[1][randNum])
    print(len(randArray[1]))
    return(randArray)
    
    
    
################### main function ##############
    
def main():
    csvArray = readCSVFile(csvFile)
    randomSample = randomlySelect(csvArray)
    screenedCSVs = getUniqueValues(randomSample)
    tempGeomFile = makeGeomPoints(screenedCSVs)
    combineTextFiles([topCSVFile,tempFilename,bottomCSVFile],outputFile)
    os.remove(tempGeomFile)
    
   
main()





### end of create_GSV_webscript.py ###