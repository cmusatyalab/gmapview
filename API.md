# GMapView API

To use the API, make sure that GMapView is in your python path and your gmapconfig.json file can be found.

----
Basic Usage

```
> from GMapView import GMapView
> gmsv = GMapView()
> gmsv.setSetting("PLOTON",True)
> gmsv.runAddress('417 S Craig St, Pittsburgh, PA 15213')
```

#### runAddress

```python
 | runAddress(addr)
```

Start the pipeline with a single street address. Accepts a string with the street address in any form that Google accepts.


#### runPt

```python
 | runPt(pt, rtname)
```

Start the pipeline with a single point. A point is a dictionary of the form: {'lat':value,'lng':value}. rtname is an arbitrary identifier string.


#### runPtLst

```python
 | runPtLst(ptlst, rtname)
```

Start the pipeline with a list of points.


#### runPt2Pt

```python
 | runPt2Pt(tptlst, rtname, numpts)
```

Start the pipeline with a list of two points that represent the beginning and end of a straight line.
This code generates intermediate numpts between the begin and end. Note this may fail or give strange results if the straight line passes somewhere too far from a location with valid streetview images.


#### getDirections

```python
 | getDirections(rtestr)
```

Start the pipeline with two street addresses and use the Google Maps walking directions
to generate the turn points for photo gathering. A rtestr is of the form: 

```
start='417 S Craig St, Pittsburgh, PA 15213',end='4125 Schenley Dr., Pittsburgh, PA 15213'
```

#### runKML

```python
 | runKML(kmlfile, rtname)
```

Start the pipeline with a kml file -- this is very limited now TODO make more general
It only works with kml files with a LinesString feature with name rtname

### Constructor Options
To specify a different configuation file:

```
> gmsv = GMapView(configfile=<path to configfile>)
```

To specify your Google Maps API Key:

```
> gmsv = GMapView(GAPIKEY=<your API Key>)
```

