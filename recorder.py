#!/usr/bin/env python
"""Raspberry Pi surveillance - recorder
Copyright (c) 2014 Patrick Van Oosterwijck
Distributed under GPL v2 license"""

import picamera
from datetime import datetime
from time import sleep
import motion
import os
import os.path
from subprocess import Popen, PIPE
import cfg


def run_recording_cycle(camera, det):
    """Run a cycle of checking for motion, and recording if motion
    is detected"""
    # Scan for motion at low resolution and use night mode for
    # high sensitivity without so much noise that it triggers
    # false motion detection
    camera.resolution = (320, 240)
    camera.exposure_mode = 'night'
    # Check for motion
    if det.motion(cfg.MOTION_THRESHOLD):
        # Record in high resolution, auto exposure
        camera.resolution = (1920, 1080)
        camera.exposure_mode = 'auto'
        # Use a timestamp as file name
        fname = os.path.join(cfg.REC_PATH, datetime.now(). \
                              strftime('rec-%Y-%m-%d-%H.%M.%S.mp4'))
        # Start the recording
        ffmpeg = Popen(['ffmpeg', '-r', str(cfg.FRAME_RATE), '-i',
                        'pipe:', '-vcodec', 'copy', fname],
                        stdin=PIPE)
        print "Recording for %d seconds to %s" % (cfg.REC_LEN, fname)
        camera.start_recording(ffmpeg.stdin, bitrate=8000000,
                                format='h264', profile='main')
        # Record for the specified amount of time
        camera.wait_recording(cfg.REC_LEN)
        # End the recording and clean up
        camera.stop_recording()
        ffmpeg.stdin.close()
        ffmpeg.communicate()
        # Go back to scanning for motion
        print "Scanning for motion..."
        det.reset()

def start_surveillance():
    """Start the surveillance"""
    camera = None
    try:
        # Endless loop
        while 1:
            # Are we in a recording time span?
            if cfg.is_recording_time():
                # Are we currently recording?
                if camera:
                    # Run a recording cycle
                    run_recording_cycle(camera, det)
                else:
                    # Start recording
                    print "Opening camera..."
                    camera = picamera.PiCamera()
                    camera.framerate = cfg.FRAME_RATE
                    # Create a motion detector object
                    det = motion.MotionDetector(camera)
                    print "Scanning for motion..."
            else:
                # We shouldn't be recording, are we?
                if camera:
                    # We have to stop recording
                    print "Closing camera..."
                    camera.close()
                    camera = None
                    det = None
                    print "Waiting until the next recording time..."
                else:
                    # Not recording, wait a while before we check
                    # again if we should
                    sleep(15)
    except KeyboardInterrupt:
        print "Done!"
    finally:
        # Make sure the camera is closed before we quit
        if camera:
            camera.close()

# Start surveillance if this is the main program
if __name__ == '__main__':
    start_surveillance()

