#!/usr/bin/python

import picamera
from time import sleep

camera = picamera.PiCamera()
print('ukladam obrazok')
camera.capture('image.jpg')

camera.start_preview()
#camera.vflip = True
#camera.hflip = True
camera.brightness = 60

print('nahravam video')
camera.start_recording('video.h264')
sleep(5)
camera.stop_recording()

