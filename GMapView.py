#!/usr/bin/env python

import sys
import os
from datetime import datetime
import time
import json
import requests
import random
from optparse import OptionParser
import logging

from GPSPhoto import gpsphoto
import googlemaps
import google_streetview.api
import xmltodict
from PIL import Image
from math import ceil
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import ImageGrid

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("gmaputillog.log"),
        logging.StreamHandler(sys.stdout)
    ]
) 

def main():
    
    ''' Main consists of two parts: the command line interface to the API 
        and a series of tests of the API. The command line options are:
        Usage: GMapView.py [options]

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

     '''


    ''' Configuring the options '''
    defpt = pt1
    defaddrstr = workaddr
    
    parser = OptionParser()
    ''' Set API Parameters '''
    parser.add_option("-d", "--headings", dest="headinglist", # d for 'direction'
        help="use STRING as headings  (comma separated list)", metavar="STRING")
    parser.add_option("-j", "--jsonconfig", dest="jsonconfig",
        help="use FILE.json as configuration file", metavar="FILE.json")
    parser.add_option("-a", "--pitch", dest="pitch",  # a for 'angle'
        help="use FLOAT as the pitch of the photo", metavar="FLOAT")
    parser.add_option("-p", "--points", dest="linepts", 
        help="use INT as # of points in a p2p test", metavar="INT")
    parser.add_option("-P", "--plot", action="store_true", dest="plot", default=None, 
        help="Plot the downloaded images")
    parser.add_option("-C", "--clean", action="store_true", dest="clean", default=None, 
        help="Delete downloaded images before exit")
        
    ''' Set Testing Variables '''
    parser.add_option("-t", "--test", dest="testlist",
        help="use STRING as test list (comma separated list); 'all' to run all tests; 'list' to get valid tests)", metavar="STRING")
    parser.add_option("-L", "--latlong", dest="latlongpair",
        help="use STRING as 'lat,long' pair (comma separated list)", metavar="STRING")
    parser.add_option("-A", "--address", dest="addrstr",
        help="use STRING as street address", metavar="STRING")
    parser.add_option("-R", "--route", dest="rtestr",
        help="use STRING as start=<START ADDRESS>;end=<END ADDRESS>", metavar="STRING")     
    (options, _) = parser.parse_args()

    ''' Instantiate the API '''
    if options.jsonconfig is not None:
        gmsv = GMapView(configfile = options.jsonconfig)
    else:
        gmsv = GMapView()
    
    ''' Override options from command line '''
    if options.plot is not None:
        gmsv.setSetting("PLOTON", options.plot)
    if options.clean is not None:
        gmsv.setSetting("CLEAN",options.clean)
    logging.info("PLOTON is {}; CLEAN is {}".format(gmsv.getSetting("PLOTON"),gmsv.getSetting("CLEAN")))
    if options.headinglist is not None:
        gmsv.setSetting("HEADINGS",options.headinglist.replace(",",";"))

    if options.linepts is not None:
        try:
            gmsv.setSetting("LINEPTS",int(options.linepts))
        except:
            logging.error("Invalid value for LINEPTS; using default. {}".format(gmsv.getSetting("LINEPTS")))
    if options.pitch is not None:
        try:
            gmsv.setSetting("PITCH",float(options.pitch))
        except:
            logging.error("Invalid value for PITCH; using default. {}".format(gmsv.getSetting("PITCH")))

    ''' Configure for testing from command line'''
    if options.latlongpair is not None:
        try:
            latlongstrlst = options.latlongpair.split(",")
            testpt = gpspt2dict([float(coord) for coord in latlongstrlst])
        except:
            logging.error("Invalid value latitude, longitude list: %s ; using default. " % (options.latlongpair,defpt))
            testpt = defpt
    else:
        testpt = defpt
    
    if options.addrstr is not None:
        addrstr = options.addrstr
    else:
        addrstr = defaddrstr
        
    if options.rtestr is not None:
        rtestr = options.rtestr
    else:
        rtestr = defrtstr
    
    ''' The following code tests the different API options by running a test case '''
    ''' Select which tests to run '''
    if options.testlist is None:
        logging.error("No tests specified; Exiting")
        sys.exit(1)
    testlist = options.testlist.split(",")            
    validtests = ['address','p2p','kml','directions','list','point']
    runtestlist = validtests if 'all' in testlist else [test for test in testlist if test in validtests]
    logging.info("Running tests: {}".format(runtestlist))
    
    ''' These exercise the main functions by running a canned test '''
    if 'list' in runtestlist:
        ''' List all of the valid tests to run '''
        logging.info("Valid Tests are: {}".format(validtests))

    if 'p2p' in runtestlist:
        ''' Get the images for each point on a straight line path between two points '''
        logging.info("Running test: {}".format('p2p'))
        gmsv.runPt2Pt([workaddrpt,cicaddrpt],'CMUSPT', gmsv.getSetting("LINEPTS"))
        
    if 'address' in runtestlist:
        ''' Get the images for a single text street address '''
        logging.info("Running test: {}".format('address'))
        gmsv.runAddress(addrstr)

    if 'kml' in runtestlist:
        ''' Get the images from a kml file -- only works for lines now '''
        logging.info("Running test: {}".format('kml'))        
        gmsv.runKML("Floor2.kml","Walnut2")
        
    if 'point' in runtestlist:
        ''' Run a single point '''
        logging.info("Running test: {}".format('point'))        
        gmsv.runPt(testpt,'TestPoint')

    if 'directions' in runtestlist:
        ''' Get the images for each turn in the walking directions between two text street addresses '''
        logging.info("Running test: {}".format('directions'))        
        gmsv.runDirections(rtestr,"CMUDIR")
    logging.info("Finished Tests")

class GMapView(object):
    def __init__(self, configfile = "./gmapconfig.json", **kwargs):
        self.configfile = configfile
        self.settings = None
        self.setDefaults()
        self.addressfile = self.settings["ADDRESSFILE"] if "ADDRESSFILE" in self.settings else "./gmapaddresses.json"

        if 'GAPIKEY' in self.settings:
            self.GAPIKEY = self.settings['GAPIKEY']
            self.gmapsclient = googlemaps.Client(key=self.GAPIKEY)
        else:
            logging.error("No GAPIKEY")
            sys.exit(1)
        if os.path.isfile(self.addressfile):
            with open(self.addressfile) as jfile:
                self.addressdict = json.load(jfile)
        else:
            logging.info("%s does not exist" % self.addressfile)
            self.addressdict = {'addresses':{}}
        self.testset = self.setTestData()
        pass
    
    def setDefaults(self,current_settings = {}, **kwargs):
        if os.path.isfile(self.configfile):
            with open(self.configfile) as jfile:
                self.settings = json.load(jfile)
        self.settings['HEADINGS'] = self.settings['HEADINGS'].replace(",",";") # Hack to allow csv for headings
    
    def setSetting(self,key,value,**kwargs):
        self.settings[key] = value

    def getSetting(self,key):
        retval = self.settings[key] if key in self.settings else None
        return retval
        
    def getSettings(self):
        return self.settings
       
    def setTestData(self,current_testset= {}, **kwargs):
        retdict = current_testset
        deftestset = {
            'address1':{'type':'ADDRESS','data':workaddr},
            'latlongpt1':{'type':"LATLONGPOINT",'data': workaddrdict },
            'gpspt1':{'type':"GPSPOINT",'data': workaddrpt },
            'address2':{'type':'ADDRESS','data':cicaddr},
            'latlongpt2':{'type':"LATLONGPOINT",'data': cicaddrdict },
            'gpspt2':{'type':"GPSPOINT",'data': cicaddrpt },
        }
        retdict.update(deftestset)
        return retdict
    
    def setTestDataValue(self,key,value,**kwargs):
        self.testset[key] = value
    
    def getTestData(self):
        return self.testset

    ''' These functions run a pipeline from different starts:
        -- Identify points to gather photos from
        -- Use GPS coordinates to get links to photos
        -- Download the photos and tag with coordinates
        -- Rename file to unique name
    '''
    
    def runAddress(self,addr):
        ''' Start the pipeline with a single street address '''
        gc = self.gmapsclient.geocode(addr)
        locdict = gc[0]['geometry']['location']
        logging.debug("Address \'{}\' is at {}".format(addr,locdict))
        self.saveAddress(addr, locdict)
        self.saveResults(self.getResultsGEO(locdict,addr))
        return locdict

    def runPt(self,pt,rtname,**kwargs):
        ''' Start the pipeline with a single point '''
        addr = "%s-latx%3.6flngx%3.6f" % (rtname,pt['lat'],pt['lng'])
        result = self.getResultsGEO(pt,addr,**kwargs)
        self.saveResults(result,**kwargs)
        return result
    
    def runPtLst(self,ptlst,rtname):
        ''' Start the pipeline with a list of points '''
        pathresult = []
        for pathpt in ptlst:
            pathresult.append(self.runPt(pathpt,rtname))
        return pathresult
        
    def runPt2Pt(self,tptlst,rtname,numpts):
        ''' Start the pipeline with a list of points with two points 
             that represent the beginning and end of a straight line.
             This code generates intermediate numpts between the begin and end
        '''
        tptptlst = [{'ppt':tptpt,'lat':tptpt[1],'lng':tptpt[0]} for tptpt in tptlst]
        ptlst = self.getPtList(tptptlst[0],tptptlst[1],numpts)
        self.runPtLst(ptlst, rtname)

    def saveAddress(self,addr,locdict):
        self.addressdict['addresses'][addr] = locdict
        with open(self.addressfile,'w') as jfile:
            json.dump(self.addressdict,jfile,indent=4)
    
    def runDirections(self,rtestr, rtname):
        self.runPtLst(self.getDirections(rtestr),rtname)
        pass
    
    def getDirections(self,rtestr):
        ''' Start the pipeline with two street addresses and use the Google Maps walking directions
            to generate the turn points for photo gathering '''
        if 'start=' not in rtestr or 'end=' not in rtestr:
            logging.error("Bad route string; Missing start or end: %s" % rtestr)
            return -1
        rtelst=rtestr.split(';')
        staddr = rtelst[0].split("=")[1] if 'start=' in rtelst[0] else rtelst[1].split("=")[1]
        dstaddr = rtelst[0].split("=")[1] if 'end=' in rtelst[0] else rtelst[1].split("=")[1]
        directions_result = self.gmapsclient.directions(staddr,
                                             dstaddr,
                                             mode="walking",
                                         departure_time=datetime.now())
        dr = directions_result[0]
        legs = dr['legs']
        turns = []
        for leg in legs:
            steps = leg['steps']
            for step in steps:
                turns.append(step['start_location'])
            turns.append(step['end_location'])
        return turns

    def runKML(self,kmlfile, rtname):
        ''' Start the pipeline with a kml file -- this is very limited now TODO make more general
            It only works with kml files with a LinesString feature with name rtname '''
        with open(kmlfile) as f:
            geodict = xmltodict.parse(f.read())
        placelst = geodict['kml']['Document']['Placemark']
        if not type(placelst) is list:
            placelst=[placelst]

        for place in placelst:
            if place['name'] == rtname:
                coord = place['LineString']['coordinates']
                coordlst = [c1.split(",") for c1 in coord.split(" ")]
                coordictlst = [{'lat':float(coord[1]),'lng':float(coord[0]),'alt':int(round(float(coord[2])))} for coord in coordlst]
        self.runPtLst(coordictlst,rtname)
    
    ''' These two functions do the bulk of the real API work '''
    def getResultsGEO(self,locdict,rtname,randomheading=False):
        ''' Get links to the right photos for a single point from the google streetview API '''
        lat,lng = locdict['lat'],locdict['lng']
        locstr = "%f,%f" % (lat,lng)
        random.seed()
        if randomheading:
            headings = "{}".format(round(random.uniform(0,359)))
        else:
            headings =  self.settings['HEADINGS']
        apiargs = {
            'size': self.settings['IMGSIZE'], # max 640x640 pixels
            'location': locstr,
            'heading': headings,
            'pitch': str(self.settings['PITCH']),
            'key': self.GAPIKEY
        }
        locdict['locstr'] = locstr
        ''' Get a list of all possible queries from multiple parameters '''
        api_list = google_streetview.helpers.api_list(apiargs)
    
        # Create a results object for all possible queries
        results = google_streetview.api.results(api_list)
        locdict['results'] = results
        locdict['rtname'] = rtname + "latx%3.5flngx%3.5f" % (locdict['lat'],locdict['lng'])
        return locdict
    
    def saveResults(self,loc,**kwargs):
        ''' Use the links from above to download the images; rename and tag them '''
        timestamp = humandate(time.time())[:-7]
        loc['results'].download_links(self.settings["IMGDIR"])
        numf = len(loc['results'].links)
        GSVHEADER='GSV-' + ''.join(e for e in loc['rtname'] if e.isalnum()) + \
                "_p" + str(self.settings['PITCH']) + "_" + timestamp + "_"
        headinglst = self.settings['HEADINGS'].split(";")
        imnamelst = []
        nfnlst = []
        for fct in range(0,numf):
            ''' Give the file a unique name '''
            try:
                fn = loc['results'].metadata[fct]['_file']
            except:
                logging.error("Filename not found -- skip point")
                continue
            ffn = os.path.join(self.settings["IMGDIR"],fn)
            newfn = os.path.join(self.settings["IMGDIR"],GSVHEADER+fn).replace("gsv_","").replace("_p","_h%s_p" % headinglst[fct])
            nfnlst.append(newfn)
            logging.debug("%s to %s" % (fn,newfn))
            if not os.path.isfile(ffn):
                logging.error(ffn," does not exist")
                continue
            os.rename(ffn,newfn)
        
            ''' Add metadata '''
            loctup = (float(loc['lat']),float(loc['lng']))
            photo = gpsphoto.GPSPhoto(newfn)
            if 'alt' in loc:
                altv = loc['alt']
            else:
                altv = 0
            info = gpsphoto.GPSInfo((loctup),alt=altv)
            photo.modGPSData(info, newfn)
            imnamelst.append(newfn)
            
        ''' Display the images '''
        if self.settings['PLOTON']:
            imlst = []
            for im in imnamelst:
                imlst.append(Image.open(im))
            ''' Get the Map '''
            if self.settings['MAPON']:
                cntr = "{0},{1}".format(loctup[0],loctup[1])
                mapim = self.getMap(cntr)
                nfnlst.append('{}/tmpmap.png'.format(self.settings['IMGDIR']))
                imlst.append(mapim)
            title = "{} at {}".format(loc['rtname'],loc['locstr'])
            self.plotImages(imlst,xpos=self.settings['XPOS'],ypos=self.settings['YPOS'],title=title)
            
        if self.settings['CLEAN']:
            logging.debug("Deleting downloaded files: {}".format(nfnlst))
            for fn in nfnlst:
                if os.path.isfile(fn):
                    os.remove(fn)
    
    def getMap(self,center, zoom=15, size ='640x640', 
               sensor ='false', mtype='roadmap',
               marker_list = [], marker_color='blue', marker_tag='W',
               output_file=None, PLOTON=False,
               **kwargs):
        url = "https://maps.googleapis.com/maps/api/staticmap?"
        output_file = output_file if output_file is not None else '{}/tmpmap.png'.format(self.settings['IMGDIR'])
        apikey = self.GAPIKEY
        urlstr = "{0}center={1}&zoom={2}&size={3}&sensor={5}&type={6}&markers=color:red%7Clabel:C%7C{7}&key={4}" \
                .format(url,center,zoom,size,apikey,sensor,mtype,center)
        for marker in marker_list:
            urlstr = "{0}&markers=color:{1}%7Clabel:{2}%7C{3}".format(urlstr,marker_color,marker_tag,marker)
        logging.debug(urlstr)
        r = requests.get(urlstr)
        with open(output_file, 'wb') as f:
            f.write(r.content)
        retim = Image.open(output_file)
        if PLOTON:
            self.plotImages([retim])
        return retim
        
    def plotImages(self,imlst,xpos=100,ypos=100,pause=None,title="TEST2",**kwargs):   
        pause = pause if pause is not None else self.settings['SHOWTIME'] if 'SHOWTIME' in self.settings else 1 
        numim = len(imlst)
        ncols = 2 if numim <= 8 else 4
        nrows = int(ceil(numim/ncols))
        fig = plt.figure(figsize=(self.settings['FIGWIDTH'],self.settings['FIGHEIGHT']))
        fig.suptitle(title)
        grid = ImageGrid(fig, 111,  # similar to subplot(111)
            nrows_ncols=(nrows, ncols),
            axes_pad=0.1,  # pad between axes in inch.
        )
        mngr = plt.get_current_fig_manager()
        mngr.window.move(xpos,ypos)

        for ax, im in zip(grid, imlst):
            ax.imshow(im)
            ax.axis('off')
        plt.ion()
        plt.show(block=False)
        plt.pause(pause)
        plt.close()
        pass

    ''' Some utility functions for generating points on a line '''
    def getPtList(self,pt1,pt2,numpts):
        ''' creates a list of numpts new points on straight line between pt1 and pt2 '''
        nn = numpts + 1
        ptlst = [pt1]
        m, b,xdist = self.getLine(pt1,pt2)
        xint = xdist/nn
        pttuplst = [(ii*xint + pt1['lat'], self.getY((ii*xint + pt1['lat']),m,b)) for ii in range(1,nn)]
        ptlst = ptlst + [{'lat':pttup[0],'lng':pttup[1]} for pttup in pttuplst]
        
        ptlst.append(pt2)
        return ptlst
    
    def getLine(self,pt1,pt2):
        ''' Pt =  {'lat': x, 'lng': y} '''
        ''' returns m=slope, b = y-intercept xdist = distance between x2 and x1 '''
        x1 = pt1['lat']
        y1 = pt1['lng']
        x2 = pt2['lat']
        y2 = pt2['lng']
        b = (x1*y2 - x2*y1)/(x1-x2)
        m =  (y1-y2)/(x1-x2)
        xdist = x2 - x1
        return m,b,xdist
    
    def getY(self,x,m,b):
        return x*m + b

''' General Utility Functions '''
def gpsdict2pt(dictpt):
    return [dictpt['lng'],dictpt['lat']]

def gpspt2dict(lstpt):
    return {'lat':lstpt[0],'lng':lstpt[1]}

def humandate(unixtime):
    retstr = datetime.fromtimestamp(unixtime).strftime('%Y-%m-%d-%H-%M-%S-%f')
    return retstr

def humandatenow():
    retstr = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S-%f')
    return retstr

''' Define some geographic locations for testing'''
workaddr = '5000 Forbes Ave, Pittsburgh, PA 15213'
cicaddr = '4720 Forbes Ave, Pittsburgh, PA 15213'
defrtstr = "start='%s';end='%s'" % (cicaddr,workaddr)
starbaddr = '417 S Craig St, Pittsburgh, PA 15213'
schenleyaddr = '4125 Schenley Dr., Pittsburgh, PA 15213'
defrtstr = "start='%s';end='%s'" % (starbaddr,schenleyaddr)

workaddrdict = {'lat': 40.44416469999999, 'lng': -79.9433725}
workaddrpt = gpsdict2pt(workaddrdict)
cicaddrdict = {'lat': 40.444837, 'lng': -79.9471412}
cicaddrpt = gpsdict2pt(cicaddrdict)
cyertaddrdict = {'lat': 40.4448675, 'lng': -79.9444167}
cicaddrpt = gpsdict2pt(cicaddrdict)

''' Penn Ave -- makes sure commas between every coordinate '''
pennptlst = [[-79.92082688848406,40.45989471062377,282.1571141195064],
                [-79.91367633243674,40.4549432329343,285.8649752131874],'Penn']

''' Walnut Street '''
walnutptlst = [[-79.93559640239131,40.45066718053887],
               [-79.93091008312071,40.45213252042862],'Walnut']

''' Craig Street '''
craigptlst = [[-79.94871048275425,40.44449150262002,274.0581036970866],
              [-79.94901117203005,40.44693977394247,278.3087578326788 ],'Craig']

pt1 = {'lat': 40.45066718053887, 'lng': -79.93559640239131}
pt2 = {'lat': 40.45213252042862, 'lng': -79.93091008312071}

if __name__ == '__main__': main()
