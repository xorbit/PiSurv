"""Configuration module for PiSurv
Copyright (c) 2014 Patrick Van Oosterwijck
Distributed under GPL v2 license"""

from ConfigParser import ConfigParser
from datetime import datetime
from dateutil.parser import parse as parsedate
import re


### Defaults

# Motion threshold (higher number: more motion needed to start recording)
MOTION_THRESHOLD = 0.7
# Path of the recordings
REC_PATH = '/var/lib/pisurv'
# Recording ZIP name
REC_ZIP = 'PiSurv.zip'
# Frame rate
FRAME_RATE = 15
# Recording length
REC_LEN = 90
# Recordings per page
REC_PER_PAGE = 5
# Record time spans
REC_TIME_SPAN = []


### Config file loader

# Time span loading and checking

def load_time_span(span_string):
    """Try to load a time span, skip invalid ones"""
    # Split into start and stop time string (separated by dash)
    m = re.match(r'^\s*(.+?)\s*-\s*(.+?)\s*$', span_string)
    # Quit if we didn't get a valid span
    if not m:
        print "Invalid time span: specify two time specs separated by '-'"
        return
    # Check that both time specs specify a valid time
    for i in range(1, 3):
        try:
            parsedate(m.group(i))
        except:
            print "Invalid time spec: %s" % m.group(i)
            return
    # Start and end time strings
    REC_TIME_SPAN.append({'start': m.group(1), 'stop': m.group(2)})
    
def is_recording_time():
    """Check whether it is a time span where we record"""
    # If no time span is specified, record continuously
    if not REC_TIME_SPAN:
        return True
    # Loop through all time spans until we find one that's active
    for ts in REC_TIME_SPAN:
        # Get the current time
        now = datetime.now()
        # We don't store the parsed objects but keep re-parsing them
        # because the parser's behavior depends on the current time
        # and date, allowing such things as day of the week to
        # be specified in the time specs.
        start = parsedate(ts['start'])
        stop = parsedate(ts['stop'])
        # Special case if start time is greater than stop time
        if start > stop:
            # Then we check if the current time is greater than the
            # start time, OR less than the end time.  Because of the
            # behavior of the dateutil parser, this makes it possible
            # to specify time spans that cross midnight.
            if now >= start or now < stop:
                return True
        else:
            # Normally, we're in the time span if now is between start
            # and stop time.
            if now >= start and now < stop:
                return True
    # We're not in any time span, don't record
    return False

# Config file attributes for parameters 

param_attr = {
    'MOTION_THRESHOLD':
        {'section': 'Recorder', 'call': 'getfloat'},
    'REC_PATH':
        {'section': 'Recorder', 'call': 'get'},
    'REC_ZIP':
        {'section': 'WebView', 'call': 'get'},
    'FRAME_RATE':
        {'section': 'Recorder', 'call': 'getint'},
    'REC_LEN':
        {'section': 'Recorder', 'call': 'getint'},
    'REC_PER_PAGE':
        {'section': 'WebView', 'call': 'getint'}
}

# Helper to load what exists in a config file

def load_from_config_file(cfg_name):
    """Load parameters from a config file, if they exist"""
    # Get a parser object
    config = ConfigParser()
    try:
        # Load the config file
        config.read(cfg_name)
        # Go through the list of parameters
        for param, attr in param_attr.iteritems():
            # Does the file speficy this parameter?
            if config.has_option(attr['section'], param):
                # Try to load it
                try:
                    globals()[param] = getattr(config, attr['call'])\
                                              (attr['section'], param)
                except:
                    print "Error parsing %s in %s, ignored" % \
                            (param, cfg_name)
        # Is there a schedule section?
        if config.has_section('Schedule'):
            # Go through the schedule
            for time_span in config.options('Schedule'):
                # Add the time span to the schedule
                load_time_span(config.get('Schedule', time_span))
    except:
        print "Failed to load %s" % cfg_name

    
### Load from /etc/pisurv.conf

load_from_config_file('/etc/pisurv.conf')

