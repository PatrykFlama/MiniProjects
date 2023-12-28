# NIFS3/b-spline
This is a implementation of natural cubic spline function integrated with pyplot with simple function editor.   

## Data format
The program is using 2 sets of files to save interpolation points and drawing arguments:  
* [./points/point{i}.txt](./points) - where _{i}_ is number of function and in every line of file there is data in format `t x y r` where `t` is parameter (curve argument), `x` and `y` are corresponding coordinates of point on curve and `r` (resolution) determines amount of segments that create the preview spline image (variables `t x y` are for the task, `r` is additional).  
* [./times/times{i}.txt](./times) files there are arguments for output function that we will draw (variables `u` form the task).  

## How to use
Run `python main.py`  
you will have 2 options - to open editor or to display function from files [./points/point{i}.tx](./points)   
In the editor (option 1):
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
  
In preview (option 2):
* _i_ to show/hide image background
* _m_ to show/hide interpolation points

to not overwrite {i}th function file simply leave it empty in the editor

### Requirements
* python 3
    * matplotlib
    * os
    * subprocess
    * cv2

