#!/usr/bin/env python
"""Raspberry Pi surveillance - recorder
Copyright (c) 2014 Patrick Van Oosterwijck
Distributed under GPL v2 license"""

import picamera
from datetime import datetime
import motion
import os
import os.path
from subprocess import Popen, PIPE


# Path of the recordings
RECPATH = '/var/lib/pisurv'
# Frame rate
FRAMERATE = 15
# Recording length
RECLEN = 100

def start_surveillance():
    """Start the surveillance"""

    print "Opening camera..."
    camera = picamera.PiCamera()
    camera.framerate = FRAMERATE

    try:
        det = motion.MotionDetector(camera)
        print "Scanning for motion..."

        while 1:
            # Scan for motion as low resolution and use night mode for
            # high sensitivity without so much noise that it triggers
            # false motion recordings
            camera.resolution = (320, 240)
            camera.exposure_mode = 'night'
            # Check for motion
            if det.motion(0.5):
                # Record in high resolution, auto exposure
                camera.resolution = (1920, 1080)
                camera.exposure_mode = 'auto'
                # Use a timestamp as file name
                fname = os.path.join(RECPATH, datetime.now(). \
                                      strftime('rec-%Y-%m-%d-%H.%M.%S.mp4'))
                # Start the recording
                ffmpeg = Popen(['ffmpeg', '-r', str(FRAMERATE), '-i',
                                'pipe:', '-vcodec', 'copy', fname],
                                stdin=PIPE)
                print "Recording for %d seconds to %s" % (RECLEN, fname)
                camera.start_recording(ffmpeg.stdin, bitrate=8000000,
                                        format='h264', profile='main')
                camera.wait_recording(RECLEN)
                camera.stop_recording()
                ffmpeg.stdin.close()
                # Go back to scanning for motion
                print "Scanning for motion..."
                det.reset()

    except KeyboardInterrupt:
        print "Done!"
        
    finally:
        camera.close()

# Start surveillance if this is the main program
if __name__ == '__main__':
    start_surveillance()
