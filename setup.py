import pip

INSTALL = True
instlst = ['googlemaps','google-streetview','xmltodict','GPSPhoto',
           'Pillow','piexif','exifread','matplotlib','gmaps']
if INSTALL:
    failed = pip.main(["install"] + instlst)