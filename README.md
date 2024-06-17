# gcodeparser
G-code to Yaskawa converter

Created for WAAM testing, but can be used as a starting point for other stuff as well. Create ARCON and ARCOFF jobs to define parameters for welding start and end + possible delays or torch cleaning/other routines between layers based on your need.

Non-polished, but working. Will most likely require modifications and at least some fine tuning if someone else wants to try on their system. Tested on Marlin g-code generated with Cura.

Usage:
 * Create an user frame for your printing plate
 * Define user frame number and tool number in gcodeparser variables
 * Modify the the JBI header to suit your robot system (remove BC if you don't have a gantry, chech the arm configuration ///RCONF
 * Create g-code file with the slicer of your course
 * Run the parser and try the generated JBI file on your robot (on your own risk, of course, so double check everything)

Known issues:
 * Might generate an extra "call arcon" at the end of the program and at the start of the program, check the generated JBI file and delete unecessary lines
 * Will not split the program, so it's easy to create too large programs for the robot to handle. If you run into errors when importing the code to robot, either
   * generate multiple JBI files manually (split the g-code before running the script)
   * modify the Python code to do this for you (main job with calls to sub jobs, each sub job containing max _n_ instructions, _n_ being whatever your controller can handle
