/* GSV2.cpp //
// Author: Andy Larkin
// Created for Perry Hystad, Oregon State University
// Date created: 2/16/2016
// This script screens images for green pixels based on a range of acceptable hue values,
// and then calculates green pixel summary statistics
*/

// header files
#include "statVals.hpp"

// abbreviations
using namespace cv;
using std::cin;
using std::cout;
using std::endl;
using std::vector;
using std::string;
using std::ofstream;

// global enum
enum pixelType { green, black };

// method prototypes

double         calcStdDev(vector<double>, double, int);
void           calcJointCountStats(Mat, statVals &);
void           calcNeighborJoinType(pixelType, pixelType, statVals &);
void           getCounters(Mat, statVals &);
vector<string> getFileNamesInDirectory(string);
void           pixelNeighbors(Mat, statVals &);
Mat            screenForGreen(Mat, string);
void           writeStatVals(string, statVals, ofstream &);


/************************ main function **********/

// main method
int main() 
{
	Mat dst;//dst image
	vector<string> fileList;
	ofstream outputfile;
	outputfile.open("filepath where summary statistics should be written, with .txt extension");
	string panoramaFolder = "folder path containing images to screen";
	string outputGreenspaceFolder = "folder path where example images can be written to";
	fileList = getFileNamesInDirectory(panoramaFolder + "*");
	

	// for eaach image to screen and analyze, screen for green pixels and calculate summary stats
	for (int i = 1; i < fileList.size(); i++) 
	{
		statVals imageStats = { 0,0,9999,0,9999,0,0,0,0,0,0,0,0,0,0,0,0,0,0 };
		Mat in_img = imread(panoramaFolder + fileList[i]);
		if (in_img.empty()) 
		{
			cout << "Error!!! Image cannot be loaded..." << endl;
			return -1;
		}
		Mat HSVoutputMat = screenForGreen(in_img, outputGreenspaceFolder + fileList[i].substr(0, fileList[i].length() - 4) + ".bmp");
		getCounters(HSVoutputMat, imageStats);
		writeStatVals(fileList[i], imageStats, outputfile);
	}
	outputfile.close();
	return 0;
}

/***************** helper functions *******************/

/* get the list of files to screen and analyze
** INPUTS:
**    directory - path to the folder containing files to process
** OUTPUTS:
**    files - list of files to screen and analyze
*/
vector<string> getFileNamesInDirectory(string directory) 
{
	vector<string> files;
	WIN32_FIND_DATA fileData;
	HANDLE hFind;
	if (!((hFind = FindFirstFile(directory.c_str(), &fileData)) == INVALID_HANDLE_VALUE)) 
	{
		cout << "looking for files" << endl;
		while (FindNextFile(hFind, &fileData)) 
		{
			files.push_back(fileData.cFileName);
		}
	} else 
	{
		cout << "couldn't find files" << endl;
	}
	FindClose(hFind);
	return files;
}


/* write green pixel summary statistics of a single image to a file
** INPUTS:
**    panId - unique id number for the image
**    inputStats - statVals struct that contains summary statistics
**    outputStream - handler for writing to the output file
*/
void writeStatVals(string panID, statVals inputStats, ofstream &outputStream) 
{
	outputStream << panID << "," << inputStats.avgHueCell << "," << inputStats.avgSatCell << ','
		<< inputStats.hueStdDev << "," << inputStats.satStdDev << "," << inputStats.maxHue << ","
		<< inputStats.maxSat << "," << inputStats.minHue << "," << inputStats.minSat << ","
		<< inputStats.percentPixelsGreen << "," << inputStats.numGreenCells << ","
		<< inputStats.numTotalCells << "," << inputStats.zStatGB << "," << inputStats.zStatGG << endl;
}


/* calculate summary statistics that are based on counting and averaging number of pixels
** INPUTS:
**    inputMat - image in matrix format
**    inputStats - pointer to a statVals struct
*/
void getCounters(Mat inputMat, statVals &inputStats) 
{
	 Size matSize = inputMat.size();
	 Vec3b pixelVal;
	 vector<double> HueVec;
	 vector<double> SatVec;
	 int minHue;
	 int maxHue;
	
	 // for each column and each row in the image matrix, sum up the number of green pixels,
	 // number of total pixels, and min and max hue and saturation
	 for (int i = 0; i < matSize.height; i++) 
	 {
		 for (int j = 0; j < matSize.width; j++) 
		 {
			 pixelVal = inputMat.at<Vec3b>(i, j);
			 float Hue = pixelVal.val[0];
			 float Sat = pixelVal.val[1];
			 float Vol = pixelVal.val[2];
			 if (Hue > 0) 
			 {
				 inputStats.sumGreenVals += Sat;
				 inputStats.sumHueVals += Hue;
				 inputStats.numGreenCells++;
				 HueVec.push_back(Hue);
				 SatVec.push_back(Sat);
				 if (Hue > inputStats.maxHue) 
				 {
					 inputStats.maxHue = Hue;
				 }
				 if(Hue < inputStats.minHue) 
				 {
					 inputStats.minHue = Hue;
				 }
				 if (Sat > inputStats.maxSat) 
				 {
					 inputStats.maxSat = Sat;
				 }
				 if (Sat < inputStats.minSat) 
				 {
					 inputStats.minSat = Sat;
				 }
			 }
			 inputStats.numTotalCells++;
		 }
	 }  
	 
	 // calculate summary statistics 
	 inputStats.avgSatCell = inputStats.sumGreenVals / (double)inputStats.numGreenCells;
	 inputStats.avgHueCell = inputStats.sumHueVals / (double)inputStats.numGreenCells;
	 inputStats.percentPixelsGreen = inputStats.numGreenCells / (double)inputStats.numTotalCells;
	 inputStats.hueStdDev = calcStdDev(HueVec, inputStats.avgHueCell, inputStats.numGreenCells);
	 inputStats.satStdDev = calcStdDev(SatVec, inputStats.avgSatCell, inputStats.numGreenCells);
	 //calcJointCountStats(inputMat, inputStats);
}


/* identify whether pixel neighbors are green for measure of spatial clustering
** INPUTS:
**     inputMat - matrix representing image values
**     inputStats - pointer to a statVals struct to store statistics for the inputMat of interest
*/
void pixelNeighbors(Mat inputMat, statVals &inputStats) 
{
	pixelType mainPixel;
	pixelType neighborPixel;
	Size matSize = inputMat.size();
	Vec3b pixelVal;
	Vec3b neighborVal;
	
	for (int i = 0; i < matSize.height; i++) 
	{
		for (int j = 0; j < matSize.width; j++) 
		{
			pixelVal = inputMat.at<Vec3b>(i, j);
			float Hue = pixelVal.val[0];
			if (Hue > 0) 
			{
				mainPixel = green;
			} else
			{
				mainPixel = black;
			}
			if (i != 0) 
			{
				// calculate top neighbor
				neighborVal = inputMat.at<Vec3b>(i-1, j);
				float Hue = neighborVal.val[0];
				if (Hue > 0) 
				{
					neighborPixel = green;
				} else
				{
					neighborPixel = black;
				}
				calcNeighborJoinType(mainPixel, neighborPixel, inputStats);
			}
			if (i != matSize.height - 1) 
			{
				// calculate bottom neighbor
				neighborVal = inputMat.at<Vec3b>(i + 1, j);
				float Hue = neighborVal.val[0];
				if (Hue > 0) 
				{
					neighborPixel = green;
				} else
				{
					neighborPixel = black;
				}
				calcNeighborJoinType(mainPixel, neighborPixel, inputStats);
			}
			if (j != 0) 
			{
				// calculate left neighbor
				neighborVal = inputMat.at<Vec3b>(i , j-1);
				float Hue = neighborVal.val[0];
				if (Hue > 0) 
				{
					neighborPixel = green;
				} else
				{
					neighborPixel = black;
				}
				calcNeighborJoinType(mainPixel, neighborPixel, inputStats);
			}
			if (j != matSize.width-1) 
			{
				// calculate right neighbor
				neighborVal = inputMat.at<Vec3b>(i, j + 1);
				float Hue = neighborVal.val[0];
				if (Hue > 0) 
				{
					neighborPixel = green;
				} else
				{
					neighborPixel = black;
				}
				calcNeighborJoinType(mainPixel, neighborPixel, inputStats);
			}
		}
	}
}


/* calculate how many neighboring pixels are green/not green
** INPUTS:
**   mainPixel - whether main pixel is green or not green
**   neighborhoodPixel - whether pixels around main pixel are green or not green
**   inputStats - ptr to the struct that will store the spatial clustering statistics
*/
void calcNeighborJoinType(pixelType mainPixel, pixelType neighborPixel, statVals &inputStats) 
{
	switch (mainPixel) 
	{
	case green:
		if (neighborPixel == green) 
		{
			inputStats.obsGG++;
		} else
		{
			inputStats.obsGB++;
		}
		break;
	case black:
		if (neighborPixel == green) 
		{
			inputStats.obsGB++;
		} else 
		{
			inputStats.obsBB++;
		}
		break;
	}
}

/* calculate spatial clustering statistics
** INPUTS:
**   inputMat - matrix version of image data
**   inputStats - ptr to the struct that will store the spatial clustering statistics
*/
void calcJointCountStats(Mat inputMat, statVals &inputStats) 
{
	Size matSize = inputMat.size();
	// J - total number of shared boundaries
	int numCorners = 4;
	int numBorderCells = (matSize.height - 2)* 2 + (matSize.width-2)*2;
	int nonBorderCells = (matSize.height - 2)*(matSize.width - 2);
	int J = (numCorners * 3 + numBorderCells * 5 + nonBorderCells * 8) / 2;
	double pG = inputStats.numGreenCells / (inputStats.numTotalCells*1.0);
	double pB = (1.0 - pG);
	double expBB = J*pB*pB;
	double expGG = J*pG*pG;
	double expBG = J*pG*pB*2;
	double mStat = 0.5*((numCorners * 3 * 2) + (numBorderCells * 5 * 4) + (nonBorderCells * 8 * 7));
	double stdDevG = sqrt((J*pG*pG) + (2 * mStat*pG*pG*pG) - ((J + 2 * mStat)*(pG*pG*pG*pG)));
	double stdDevGB = sqrt((2 * (J + mStat)*pB*pB) -(4*(pG*pG*pB*pB)*(J+2*mStat) ));
	pixelNeighbors(inputMat, inputStats);
	inputStats.zStatGG = (inputStats.obsGG - expGG) / stdDevG;
	inputStats.zStatGB = (inputStats.obsGB - expBG) / stdDevGB;
}


/* calculate standard deviation
** INPUTS:
**    valVec - vector input values
**    avgVAl - mean of the valVec
**    sampSize - sample size
*/
double calcStdDev(vector<double> valVec, double avgVal, int sampSize) 
{
	double dev = 0;
	double dev2 = 0;
	double sqDiff = 0;
	for (int index = 0; index < valVec.size(); index++) 
	{
		sqDiff = (valVec[index] - avgVal)*(valVec[index] - avgVal);
		dev += sqDiff;
	}
		dev2 = sqrt(dev / (double)(sampSize - 1.0));
		return dev2;
}



/* screen image for green pixels
** INPUTS:
**    in_img - image in matrix format
**    outputFile - filepath to write a screened image, if not commented out
*/
Mat screenForGreen(Mat in_img, string outputFile) 
{
	Mat five_by_five_element(3, 3, CV_8U, Scalar(1));
	Mat grayImg, hist, rgbOutputMat, openedImage, closedImage;
	cvtColor(in_img, grayImg, CV_RGB2HSV);
	cv::Mat output, outputMat;
	cv::inRange(grayImg, cv::Scalar(57, 26, 0), cv::Scalar(98, 255, 255), output);
	//cv::imshow("output", output);
	morphologyEx(output, openedImage, MORPH_OPEN, five_by_five_element);
	morphologyEx(openedImage, closedImage, MORPH_CLOSE, five_by_five_element);
	grayImg.copyTo(outputMat, openedImage);
	//cvtColor(outputMat, rgbOutputMat, CV_HSV2RGB);
	//cout << "writing output greenspace image" << endl;
	//imwrite(outputFile, rgbOutputMat);
	//cout << "completed creating greenspace image" << endl;
	return outputMat; 
}



// end of GSV2.cpp