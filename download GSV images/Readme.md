# GSV_NDVI_Comparison #

Scripts to download GSV images from Google Street View API

**Author:** [Andrew Larkin](https://www.linkedin.com/in/andrew-larkin-525ba3b5/) <br>
**Affiliation:** [Oregon State University, College of Public Health and Human Sciences](https://health.oregonstate.edu/) <br>
**Principal Investigator:** [Perry Hystad](https://health.oregonstate.edu/people/perry-hystad) <br>
**Date last modified:** September 23rd, 2018

**Summary** <br>
These scripts are deisgned to populate a google map with locations, request Google Street View image ids from the populated locations, and download Google Street View imagery given the corresponding image ids

**Processing Scripts** <br>
[**create_GSV_webscript.py**](create_GSV_webscript.py) - combine the text files get_PanID_Bottom_Half.txt and	get_PanID_Top_Half.txt into a single web browsing html page <br>
[**downloadGSV.py**](downloadGSV.py) - download street view images using the Google Earth Engine API <br>
[**get_PanID_Bottom_Half.txt**](get_PanID_Bottom_Half.txt) - bottom half of html file used to get image ids <br>
[**get_PanID_Top_Half.txt**](get_PanID_Top_Half.txt) - top half of html file used to get image ids
