#!/usr/bin/env python
# -*- coding: utf-8 -*- 
import requests
import RPi.GPIO as GPIO
import time
import subprocess


GPIO.setmode(GPIO.BOARD)

TRIG = 16
ECHO = 18
i = 0

GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)
GPIO.setup(12, GPIO.OUT)
GPIO.setup(11, GPIO.OUT)
GPIO.output(TRIG, False)


time.sleep(2)

url = "http://192.168.0.7:7000/post/?location=hall"

try:
    print("System Started")
    while True:
        GPIO.output(TRIG, True)
        time.sleep(0.00001)
        GPIO.output(TRIG, False)

        while GPIO.input(ECHO) == 0:
            pulse_start = time.time()

        while GPIO.input(ECHO) == 1:
            pulse_end = time.time()

        pulse_duration = pulse_end - pulse_start

        distance = pulse_duration * 17150

        distance = round(distance+1.15, 2)

        if distance <= 45:
            print("in distance")
            GPIO.output(12, GPIO.HIGH)
            subprocess.call(["fswebcam", "-r", "640×480", "image2.jpg"])
            files = [
                ('file', open("image2.jpg", 'rb'))
            ]
            print("pic captured")
            response = requests.request("POST", url, files=files)
            print("response sent")
            print(response.text.encode('utf8'))
            GPIO.output(12, GPIO.LOW)
            print("green red light low")
            GPIO.output(11, GPIO.HIGH)
            print("green light high")
            time.sleep(4)
            GPIO.output(11, GPIO.LOW)
            print("green light low")
            print("out of loop")

except KeyboardInterrupt:
    GPIO.cleanup()


