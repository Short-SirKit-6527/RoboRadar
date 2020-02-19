# RoboRadar
Robot position display software for FRC. This project was made to help drivers visualize where robots are located on the field using the odometry available from WPILIB.

## Usage
After installation, there are two main ways to use the program. Independent usage is when you use the program as standalone. It will create it's own window and run as you would expect. Dependent usage is when the program is used in another program. An example would be using this as a plugin for WPILIB Shuffleboard (this is not yet implemented, but is planned).
### Installation
Roboradar must be setup on **both** the driverstation and the robot.
#### Driver Station
Run `pip install roboradar` to install. Then configure the RoboRadarConfig.json. This can be done globally by editing the copy in site-packages or locally by creating a proper config file in the current working directory and starting roboradar there. Most of the defaults work fine, but you should change the team number.
It is highly recommended to set the video engine to pygame in the config file. to do this, first download the most recent version via the instructions from https://www.pygame.org/wiki/GettingStarted, then change the video engine to "pygame" in the config file.
#### Robot
Currently, teams must send the data back to driver station manually by creating network tables instances. Java and C++ libraries will come soon. Labview support is not a priority (Submit a pull request if you get it working).
### Independent Usage (running as a standalone program)
Run the command `py -m roboradar`. The terminal will ask for a team number if it has not been set in the config file.
If you do not want a terminal to show up, make a shortcut with the path set to `pythonw -m roboradar`. If you do this you **MUST** set the team number using the config file.
### Dependent Usage (running within another program)
This will vary greatly depending on implementation. In general, you will not use a config file (it will still be used for setting default options however). Instead, you will typically pass the data when you interface with it. (TODO: Better explanation of how to use independent)
## Configuration
Here is a list of each configuration section, along with a description of what each option does.
### Video
Video ouput options. Most options only affect independent mode.
* ENGINE
  * Default: "pygame"
  * Sets the video engine to use when drawing the graphics.
* FPS
  * Default: 60
  * Number of FPS to run the screen at. Recommended 30, 60, or the refresh rate of the monitor.
* SCREEN_DIMENSIONS
  * Default: [480,640]
  * Set the starting screen width and height. The first number is width, the second is height.
* ANTIALIASING
  * Default: true
  * Enables or disables antialiased polygons and lines. Disable if you have performance issues.
* FILLED_POLYGONS
  * Default: true
  * Enable/disable filled polygons giving everything a wireframe look. Disabling is NOT RECOMMENDED.
### Team
Team setting options. These will configure how it will connect to robots and display itself, among other things.
* NAME
  * Default: null
  * Set the team name to display. This is only a visual effect.
* NUMBER
  * Default: 0
  * Sets the team number to use for connecting to robots and network tables. It is highly recommended to change this before use.
### Robot
Robot related options. These set up what type of robot will be used.
* NAME
  * Default: null
  * Name of robot type to connect to. This has yet to be implemented.
* IP_ADDRESS_FORMAT
  * Default: "10.{}.{}.2"
  * Format to use for the IP address. The two {} will be replaced with sections of the team number. (for example, team 6527 will become 10.65.27.2)
* IP_ADDRESS
  * Default: null
  * Override for the IP address. Recommended only if using a non standard IP scheme.
### Field
Field related options. These set up what field will be show behind the robots.
* NAME
  * Default: "FRC_2020"
  * Name of the field to load.
### System
System related options. These change internal settings in the system.
* FORCE_RUN_AS_MODULE
  * Default: true
  * Forces \_\_init\_\_.py to be run as a module. Not really an issue when running as specified, but useful when testing in something like IDLE. This will make the program restart itself as a module.
