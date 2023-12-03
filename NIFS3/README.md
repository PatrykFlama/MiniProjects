# NIFS3/bspline

## Description
This is a simple implementation of natural cubic spline function integrated with pyplot.   
For fun (and speed) the module computing nifs3 is written in C++ and executed from python code.  
As for now there are 2 versions of this program:
1. interpolation points are choosen separately and saved in file, then plotted in another program
   * `extract_points.py`
   * `main.py`
2. pyplot window is interactive and points will be saved after exiting the program
    * `sandbox.py`

## Requirements
* python 3
    * matplotlib
    * os
    * subprocess
    * cv2
* gcc

## Usage
compile `calc_nifs3.cpp` to `calc_nifs3.exe`
1. run `python extract_points.py` then `python main.py` 
2. run `python sandbox.py`

