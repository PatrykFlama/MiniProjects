# NIFS3/b-spline

## Description
This is a implementation of natural cubic spline function integrated with pyplot with simple function editor.   
It is possible to save and load functions from files [./points/point{i}.txt](./points) - where {i} is number of function and in every line of file there is a point in format: `t x y r` where `t` is parameter, `x` and `y` are coordinates of point and `r` determines amount of segments that create the preview spline image.  
In the [./times/times{i}.txt](./times) files there are arguments for output function that we will draw.  

## How to use
Run `python main.py`  
you will have 2 options - to open editor or to display function from files [./points/point{i}.tx](./points)   
In the editor:
* left click to add point
* right click to remove point
* _escape_ to exit editor and save points to files
* _enter_ to start new function
* _backspace_ to remove last function or clear active one
* _i_ to show/hide image background
* _m_ to show/hide points
* _d_ to enable/disable drawing
* _=_ to slightly increase resolution
* _8_ to increase resolution
* _-_ to slightly decrease resolution
* _/_ to decrease resolution
  
In preview:
* _i_ to show/hide image background
* _m_ to show/hide interpolation points

to not overwrite {i}th function file simply leave it empty in the editor

## Requirements
* python 3
    * matplotlib
    * os
    * subprocess
    * cv2

