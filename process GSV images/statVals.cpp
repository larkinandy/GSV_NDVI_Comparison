/* statVals.cpp
** Author: Andrew Larkin
** Created for Perry Hystad, Oregon State University
** Date created: 3/24/2016
** custom data structure for calculating and storing summary statistics
*/


// header files
#include <opencv2\core\core.hpp>
#include <opencv2\highgui\highgui.hpp>
#include <iostream>
#include <opencv2\features2d\features2d.hpp>
#include <opencv2\imgproc\imgproc.hpp>
#include <vector>
#include "statVals.hpp"
#include <Windows.h>
#include <fstream>

using namespace cv;
using std::cin;
using std::cout;
using std::endl;
using std::vector;
using std::string;
using std::ofstream;


// end of statVals.cpp