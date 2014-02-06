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
import cfg


def start_surveillance():
    """Start the surveillance"""

    print "Opening camera..."
    camera = picamera.PiCamera()
    camera.framerate = cfg.FRAME_RATE

    try:
        det = motion.MotionDetector(camera)
        print "Scanning for motion..."

        while 1:
            # Scan for motion as low resolution and use night mode for
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

    except KeyboardInterrupt:
        print "Done!"
        
    finally:
        camera.close()

# Start surveillance if this is the main program
if __name__ == '__main__':
    start_surveillance()

