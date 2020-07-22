# GMapView

GMapView is a simple tool to allow downloading and viewing images from Google StreetView using different ways of expressing locations. It is implemented as a class for use in other modules and has a command line interface for direct access. This version has been tested with python3 on Ubuntu 18.04 and Windows 10. *The example commands below assume that your default python installation is python3. GMapView will not work with python2 and given the [sunsetting of python2 support](https://www.python.org/doc/sunset-python-2/), there are no plans to backport.*

## Prerequisites and Setup

To use GMapView, you will need a googlemaps [API key](https://developers.google.com/maps/documentation/javascript/get-api-key) from Google. Then clone this repository, change directory into gmapsview and run:

```
> python setup.py
> cp gmapconfig.json.template gmapconfig.json
```

Edit **gmapconfig.json** to add your API key and change any other parameters. The location for downloaded images is controlled by the **IMGDIR** setting in this file. 

---

Now test your installation with:

```
> python GMapView.py -t list
```

This should print a list of the accepted "tests" that GMapView understands. It will also validate that all of the prerequisites are installed. To actually run the API, try:

```
> python GMapView.py -t point
```

If successful, you should see four new images in your IMGDIR. If you'd like to have these images displayed, try:

```
> python GMapView.py -t point --plot
```

Each test has a default location and most can be overridden with a custom location. The current list of valid tests is * 'address', 'p2p', 'kml', 'directions', 'point', 'all'*.
 A few more command line examples:

```
> python GMapView.py -t address -A '4125 Schenley Dr., Pittsburgh, PA 15213' -P
> python GMapView.py -t point -L 40.45213252042862,-79.93091008312071 -P
> python GMapView.py -t directions -R start='417 S Craig St, Pittsburgh, PA 15213',end='4125 Schenley Dr., Pittsburgh, PA 15213' -P
```

The full set of commmand line options are:

```
Usage: python GMapView.py [options]

Options:
  -h, --help            show this help message and exit
  -d STRING, --headings=STRING
                        use STRING as headings  (comma separated list)
  -j FILE.json, --jsonconfig=FILE.json
                        use FILE.json as configuration file
  -a FLOAT, --pitch=FLOAT
                        use FLOAT as the pitch of the photo
  -p INT, --points=INT  use INT as # of points in a p2p test
  -P, --plot            Plot the downloaded images
  -C, --clean           Delete downloaded images before exit
  -t STRING, --test=STRING
                        use STRING as test list (comma separated list); 'all'
                        to run all tests; 'list' to get valid tests)
  -L STRING, --latlong=STRING
                        use STRING as 'lat,long' pair (comma separated list)
  -A STRING, --address=STRING
                        use STRING as street address
  -R STRING, --route=STRING
                        use STRING as start=<START ADDRESS>;end=<END ADDRESS>
```

The API further allows flexibility in specifying point to point routes and KML files. KML parsing is relatively primitive at this time. API Documentation is [here](API.md).

---
The configuration parameters for the json file are:

```
{
	"GAPIKEY":"<YourAPIKey>",
	"IMGDIR":"YourImageDirectory",
	"IMGSIZE":"600x300", 		# Max size is 640x640
	"CLEAN":false,			# Delete the downloaded files before exiting
	"HEADINGS":"0,90,180,270",	# Compass direction to take the images from.
	"PITCH":0,			# The vertical angle to take the image from 
	"LINEPTS":4,			# For point to point, the number of points on the line from start to end
	"PLOTON":false, 		# Display the images 
	"SHOWTIME":4,			# How long (in seconds) each plot should display
	"MAPON":true,			# Show a map marking the location in the plot	
	"XPOS":100,			# The X screen position for plots
	"YPOS":100,			# The Y screen position for plots
	"FIGWIDTH":15,			# Width of the plot
	"FIGHEIGHT":15,			# Height of the plot
	"ADDRESSFILE":"./gmapaddresses.json"	# The file to use as a cache for searched addresses.
}
```

When using the API, any of these parameters can be overridden at runtime using the setSetting(key,value) method.
