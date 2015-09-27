# jon klein, jtklein@alaska.edu
# utility to display landsat-8 images for the decision theater north
# created during fairbanks 2015 hackathon
# mit license

import datetime
import time
import subprocess
import pdb 
import re
import ast
import os
import argparse
from PIL import Image, ImageDraw, ImageFont

from geopy.geocoders import Nominatim

LATITUDE = 0
LONGITUDE = 1
LANDSAT_DATA_PATH = "/home/kleinjt/landsat/"
LABEL_COLOR = '#FFFFFF'
LABEL_FONT = 'FreeMono.ttf'
LABEL_BASE = (500, 500)
LABEL_SIZE = 400

PROCESSED_DIR = 'processed'
ANNOTATED_DIR = 'annotated'

ansi_escape = re.compile(r'\x1b[^m]*m') # regular expression to strip coloring from landsat return


# return (latitude, longitude) tuple from an address or place name 
def get_latlong(place):
    geolocator = Nominatim()
    location = geolocator.geocode(place)
    return (location.latitude, location.longitude)

# search for landsat records centered on a location
def landsat_search(location, startdate = None, enddate = None, maxcloud = None, maxreturns = 16, matchpath = True):
    latlong_tuple = get_latlong(location)
    latitude = str(latlong_tuple[LATITUDE])
    longitude = str(latlong_tuple[LONGITUDE])


    command = ['landsat', 'search']
    command.append('--lat')
    command.append(latitude)
    command.append('--lon')
    command.append(longitude)

    if maxcloud:
        command.append('--cloud')
        command.append(str(maxcloud))

    if maxreturns:
        command.append('--limit')
        command.append(str(maxreturns))
                
    if startdate:
        command.append('--start')
        startdate = startdate.strftime("%m/%d/%Y")
        command.append(startdate)

    if enddate:
        command.append('--end')
        enddate = enddate.strftime("%m/%d/%Y")
        command.append(enddate)
    
    print ' '.join(command)
    search = subprocess.check_output(command)
    search = ansi_escape.sub('', search)
    
    scene_dict = ast.literal_eval('\n'.join(search.split('\n')[1:-4]))

    assert scene_dict['status'] == 'SUCCESS'
    landsat_results = scene_dict['results']
    
    landsat_result_dates = [time.strptime(lr['date'], "%Y-%m-%d") for lr in landsat_results]

    # sort landsat results by date
    landsat_records = [landsat_results for landsat_result_dates, landsat_results in sorted(zip(landsat_result_dates, landsat_results))]
  
    # the landsat may fly over a spot using different paths, we might want to limit the search to records that use the same path
    if matchpath:
        path_matches = []
        latest_path = landsat_records[-1]['path']
        for record in landsat_records:
            if record['path'] == latest_path:
                path_matches.append(record)

        landsat_records = path_matches
    print('finished search') 
    return landsat_records

def landsat_download(landsat_records, bands = None, process = True, pansharpen = False):
    command = ['landsat', 'download']

    if process:
        command.append('--process')

    if pansharpen:
        command.append('--pansharpen')

    if bands:
        command.append('--bands')
        command.append(bands)

    for record in landsat_records:
        print('adding sceneID {} to download list'.format(record['sceneID']))
        command.append(record['sceneID'])
    
    print ' '.join(command)
    print('starting download and processing, this may take some time...')
    download = subprocess.check_output(command)
    print('download and processing complete')


# find filename for landsat record image, create directory structure if it doesn't exist
def record_image_filename(record, imgdir, band = '432'):
    filename = '{}_bands_{}.TIF'.format(record['sceneID'], band)
    directory = os.path.join(LANDSAT_DATA_PATH, imgdir, record['sceneID'])
        
    if not os.path.exists(directory):
        os.makedirs(directory)

    full_filename = os.path.join(directory, filename)
    return full_filename

# annotate processed images with date and location, then save them to ANNOTATED_DIR
def annotate_landsat_images(landsat_records, bands = '432', location = '', downsize = .5):
    for record in landsat_records:
        print('annotating {}'.format(record['date']))
        filename = record_image_filename(record, PROCESSED_DIR)
        outfile = record_image_filename(record, ANNOTATED_DIR) 

        record_file = open(filename, 'rb')
        record_image = Image.open(filename)
        draw = ImageDraw.Draw(record_image)
        font = ImageFont.truetype(LABEL_FONT, 144)
        
        label = 'Landsat {}\n{}, Band {}\n{}'.format(record['sat_type'], record['date'], bands, location)
    
        draw.text(LABEL_BASE, label, fill = LABEL_COLOR, font = font)
       
        # resize image for less memory usage..
        if downsize:
            newsize = (record_image.width * downsize, record_image.height * downsize)
            image.resize(newsize)

        record_image.save(outfile, 'TIFF') 

if __name__ == '__main__':
    # see https://pyglet.readthedocs.org/en/latest/programming_guide/windowing.html

    #display = platform.get_display(display_name)
    #window = pyglet.window.Window(display = display)

    #screens = display.get_screens()
    #img = pyglet.image.load('test.jpg')
    location = 'Chiniak, AK'
    startdate = datetime.datetime(2014, 1, 1)

    records = landsat_search(location, startdate = startdate, maxreturns = 20)
    landsat_download(records)
    annotate_landsat_images(records, location = location)
    pdb.set_trace()
