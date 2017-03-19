/* statVals.hpp
** Author: Andrew Larkin
** Created for Perry Hystad, Oregon State University
** Date created: 3/24/2016
** header file for struct that holds summary statistics of green space screening
*/

#ifndef STATVALS_HPP
#define STATVALS_HPP

struct statVals
{
	int numGreenCells, //1
		numTotalCells, //2
		minHue, //3
		maxHue, //4
		minSat, //4
		maxSat; //5
	double avgSatCell, //6
		avgHueCell, //7
		sumGreenVals,//9
		sumHueVals,//10
		percentPixelsGreen,//11
		hueStdDev,//12
		satStdDev,//13
		expGB,//14
		expGG,//15
		obsGB,//16
		obsGG,//17
		obsBB,//18
		zStatGG,
		zStatGB;
		
};

#endif


// end of statVals.hpp