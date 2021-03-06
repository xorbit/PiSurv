# PiSurv: Video surveillance for the Raspberry Pi

[Raspberry Pi]:http://raspberrypi.org
[camera module]:http://www.raspberrypi.org/archives/tag/camera-module
[picamera]:https://github.com/waveform80/picamera/
[Motion]:http://www.lavrsen.dk/foswiki/bin/view/Motion/WebHome
[VLC]:http://www.videolan.org/
[FFmpeg]:http://www.ffmpeg.org/
[Libav]:http://libav.org/
[Debian]:http://www.debian.org
[Raspbian]:http://www.raspbian.org/
[Flask]:http://flask.pocoo.org/
[python-daemon]:https://pypi.python.org/pypi/python-daemon/
[daemon]:http://libslack.org/daemon/
[article about getting a Python script to run in the background]:http://blog.scphillips.com/2013/07/getting-a-python-script-to-run-in-the-background-as-a-service-on-boot/
[start-stop-daemon]:http://man.he.net/man8/start-stop-daemon
[PIL]:http://www.pythonware.com/products/pil/
[numpy]:http://www.numpy.org/
[dateutil]:http://labix.org/python-dateutil

## What is it?

This is a little video surveillance package for the [Raspberry Pi].  It is specifically made for use with the Pi's [camera module], and uses the excellent [picamera] Python module.  It monitors the camera view, and if motion is detected, it records a video.  A web viewer is included, which allows you to view the recordings in a web browser, download them or delete them.  There is a powerful scheduling feature that allows you to specify time spans when the surveillance should be active.

The reason I created this is that most surveillance projects I've seen for the Raspberry Pi use the standard (and quite nice) [Motion] package.  This works great on regular computers, unfortunately on the Pi it doesn't succeed in recording video at more than 2 frames per second or so, because it uses the CPU to encode the video stream.  The stream coming from the Pi's [camera module] is already encoded by the GPU, resulting in acceptable video quality and frame rates even at high resolutions.  The [picamera] Python module provides easy access to this powerful capability.  This project wraps all this nice technical power into and easy to use package for end users.

## Challenges

I encountered plenty of challenges on the way.  Since the purpose of the Pi is to be educational, I'll explain some of the problems I ran into and how I dealt with them.  If you're not interested and just want to get on with running the software, you can skip this section.

### Low light noise

Initially I had lots of false triggers due to noise in the image when dealing with low-light situations.  I solved this by switching the camera module to 'night' mode during detection.  The disadvantage is that motion detection is significantly slower, due to the long exposure times in night mode.  Another artifact of this is that at the start of the recording, you notice the module switching back to 'auto' mode, which usually results in a light start with sudden darkening.  I would have thought that in auto mode, the camera module would automatically switch to night mode in low light conditions, but this does not seem to be the case, making this hack necessary.

### The video stream

I liked the idea of using an H.264 stream from the camera module because this is one of the codecs supported by HTML5 and as such can play natively in most modern browsers.  I had expected no issues there, but there were plenty.  Turns out the stream coming from the camera is a raw H.264 stream, it has no container.  If I recall correctly, only [VLC] knew how to do anything with the generated files.  Not one browser was capable of dealing with it.  So I needed a way to package this raw stream in an MP4 container.  I immediately thought of [FFmpeg], the swiss army tool for codecs.

### Libav

My first surprise when I ran FFmpeg was to see a message saying that FFmpeg was deprecated and to use [Libav] instead.  I almost fell over.  Upon investigation I found out that Libav is a fork or FFmpeg, favored by [Debian] (and by extension [Raspbian]).  Well OK, I don't care what it's called.  So figured out the Libav options to package my H.264 stream into an MP4 container, while just copying the video stream.  I got an MP4 file.  It still didn't work.

### Duration: 0 seconds, Frame rate: 3834 frames per second

I figured out the basic problem with the raw H.264 stream was that it contained no information about the length of the video or the frames per second to play it at.  That's why I needed to specify a parameter to let Libav know what the frame rate was, so it could put it in the MP4 file and the players would be happy.  Only it wasn't working.  The MP4 files still reported rediculous things like 0 second duration and 3834 fps.  After pulling out a sufficient amount of hair and doing some Googling, I found others who had this problem.  It seems the Libav tool was just ignoring the bit rate parameter.  The suggested solution was to get the latest official FFmpeg and try that.

### FFmpeg

I got the FFmpeg source and compiled it.  And compiled it.  And compiled it some more.  It took hours.  But when it was finally done, the wait had been worth it: it generated MP4 files with sane lengths and bit rates!  Only, when serving them from my Raspberry Pi with my Python script, they still didn't play in browsers!

### Nginx

I had developed my simple little web viewer with [Flask].  I had figured out how to serve static files from the directory where the recordings were stored.  They started loading, but after a certain number of megabytes, the connection would error out.  I fought with this for a while.  Eventually I tried what happened if I served the same web page and video file on my web server running Nginx.  It worked!  I still don't know why it failed with Flask.  Maybe it tried to load the file in memory instead of streaming it, maybe I needed to configure something differently, I don't know.  I installed Nginx on my Raspberry Pi instead.  It is light, easy to configure and works well.

### Daemons and init scripts

Ah, this is so much fun every time I try to do it (NOT!).  I tried to use Python's [python-daemon] module.  It wouldn't work with the recording script.  It didn't report anything was wrong.  It would just not do anything, no idea why.  I tried the [daemon] program.  Same thing!  It didn't give any messages of any kind, it just didn't work.  Eventually I found this [article about getting a Python script to run in the background], which uses the [start-stop-daemon] program.  Using that as a template finally got it working!

## Dependencies

This package requires the [PIL], [numpy], [picamera], [dateutil] and [Flask] Python modules.  On [Raspbian], you should be able to install these with:

```bash
sudo apt-get install python-imaging python-numpy python-picamera python-dateutil python-flask
```

It also requires Nginx, or another web server.  Nginx can be installed on Raspbian using:

```bash
sudo apt-get install nginx
```

The installer automatically sets up Nginx correctly for use with this package.  If you want to use another web server, you have to configure it to serve requests for files under the `/rec` path from `/var/lib/pisurv`, and pass all other requests on to `localhost:5005` so they can be served by the [Flask] script.

Another external dependency is [FFmpeg].  As explained above, the one included in the [Raspbian] repository does not work.  You can download the source from the [FFmpeg] developers and compile it.  A cross compiler on a fast machine would be best for this, since doing it on the Raspberry Pi takes hours.  To alleviate this problem, I have included the binary I compiled in the `/deps` directory, and the installation script will install this to `/usr/local/bin`, unless it already exists there.

## Installation

You should be able to install the package with:

```bash
sudo ./INSTALL.sh
```

This will install everything, configure the init system to start the program on boot, and start it immediately.

## Configuration

The package configuration can be customized using the configuration file `/etc/pisurv.conf`.  If this file does not exist on installation, the install script will create one containing default values.  The configuration file contains settings such as the motion threshold, recording path, recording length and frame rate, and options for the web viewer.  The default configuration file contains comments that can help you to set this up.

By default, the camera is monitored for motion continuously.  To use the scheduling feature, you can add a `[Schedule]` section to the configuration file, and add keys with values that specify time spans to this section.  The key names do not matter and can be chosen to clarify the user's intent.  The time spans are two time specifications that the `python-dateutil` package can parse and separated by a dash: `-`.

For example, a configuration that records every day from noon till 1 PM, and on Tuesdays from 7:15 PM till 10 PM could look like this:

```
[Schedule]
NOON = 12pm - 1pm
MEETING_TUE = tuesday 7:15 pm - tuesday 10:00 pm
```

You have to make sure to use the same precision in the time specification for both start and stop times, since they are parsed separately.  For instance, daily recording spans should not contain any date or day of week references at all.  Once-per-week specifications need to contain a week day for both start and stop times.  The system is not smart enough to infer what you mean when you only specify a weekday for the start time, for instance.  When specifying an absolute date, a full date needs to be present for both the start and stop times.  Failing to keep start and stop times consistent this way will produce unpredictable results.

## Running the program

The daemon can be started and stopped with:

```bash
sudo service pisurv start
sudo service pisurv stop
```

To stop the daemon from loading at boot time, use:

```bash
sudo update-rc.d pisurv remove
```

If you want to have it start on boot again, use:

```bash
sudo update-rc.d pisurv defaults
```

## Known issues / planned features

* Needing a custom FFmpeg sucks.  Would be great if [Raspbian] would include the official one from the [FFmpeg] developers, or if the [Libav] developers fixed their problem.
* Right now, there is no limit on the number of recordings.  You have to clear them manually.  It would be nice if a maximum size, number of recordings or age could be specified and old recordings would be removed automatically.
* Motion detection could use some improvement.  It isn't as good as [Motion]'s.
* The web viewer could use some style improvements.
* New recordings show in the web viewer as broken videos, until they are complete.  It would be nicer if they only showed up after they were done recording.
* A .deb package would be great.

