"""Motion detection module for PiSurv
Copyright (c) 2014 Patrick Van Oosterwijck
Distributed under GPL v2 license"""

from PIL import Image, ImageChops
import numpy
import io


class MotionDetector(object):
    """Motion detector class"""

    def __init__(self, camera):
        """Constructor"""
        self.camera = camera
        self.reset()

    def reset(self):
        """Reset detection to initial conditions"""
        self.image = None
        self.skip = 3

    def image_entropy(self, img):
        """Image entropy function from:
        http://stackoverflow.com/questions/5524179/how-to-detect-motion-
        between-two-pil-images-wxpython-webcam-integration-exampl"""
        w,h = img.size
        a = numpy.array(img.convert('RGB')).reshape((w*h,3))
        h,e = numpy.histogramdd(a, bins=(16,)*3, range=((0,256),)*3)
        prob = h/numpy.sum(h) # normalize
        prob = prob[prob>0] # remove zeros
        return -numpy.sum(prob*numpy.log2(prob))

    def entropy(self):
        """Capture an image and generate the motion entropy compared
        to the last image"""
        stream = io.BytesIO()
        self.camera.capture(stream, format='png', use_video_port=True)
        stream.seek(0)
        image = Image.open(stream)
        if self.skip > 0:
          e = 0.0
          self.skip -= 1
        else:
          e = self.image_entropy(ImageChops.difference(image, self.image));
        self.image = image
        return e;

    def motion(self, th):
        """Return whether motion was detected for the specified threshold"""
        return self.entropy() >= th

