# -*- coding: utf-8 -*-
import RPi.GPIO as GPIO
import time
import numpy as np
import cv2
from datetime import datetime
import httplib, urllib, os, glob, requests , urllib2
import dht11
fire = 0
gas = 0
temperature = 0 
humidity = 0
Doorbell =4
pir = 21
firesensor = 18
gassensor = 23

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)


GPIO.setup(Doorbell , GPIO.IN)
GPIO.setup(pir , GPIO.IN)
GPIO.setup(gassensor, GPIO.IN)
GPIO.setup(firesensor , GPIO.IN)

GPIO.setup(7, GPIO.OUT)
p = GPIO.PWM(7, 50)
p.start(2.5)
instance = dht11.DHT11(pin = 14)


global previous_state
previous_state = False
global current_state
current_state = False

GPIO.setup(5, GPIO.OUT)
GPIO.output(5, GPIO.LOW)
GPIO.setup(6, GPIO.OUT)
GPIO.output(6, GPIO.LOW)
GPIO.setup(10, GPIO.OUT)
GPIO.output(10, GPIO.LOW)
base_url = "http://smartsecurity.thesmartbridge.com/API/update?key=71486723251"

def doorcontrol():
    url = "http://smartsecurity.thesmartbridge.com/API/get_talkback?userkey=71486723251"
    connect = urllib2.urlopen(url)
    response= connect.read()
    
    #response = urllib.urlopen(url).read()
    print response
    try:

        if response == "DOOROPEN":
            p.ChangeDutyCycle(12.5)  #180°
            
        if response  == "DOORCLOSE":
            p.ChangeDutyCycle(2.5) #0°
            
        if response  == "LIGHT1ON":
            GPIO.output(5,GPIO.HIGH)
            print "light1 is on"
        
        if response  == "LIGHT1OFF":
            GPIO.output(5,GPIO.LOW)
            print "light1 is off"
            
        if response  == "LIGHT2ON":
            GPIO.output(10,GPIO.HIGH)
            print "light2 is on"
        
        if response  == "LIGHT2OFF":
            GPIO.output(10,GPIO.LOW)
            print "light2 is off"
            
        if response  == "FANON":
            GPIO.output(6,GPIO.HIGH)
            print "fan is on"

        if response == "FANOFF":
            GPIO.output(6,GPIO.LOW)
            print "fanoff is off"
    
        
    except keyboardinterrupt:
      p.stop()


def sensors():
    
   
    gas = GPIO.input(gassensor)
    print " GAS STATUS " +str(gas)
    fire = GPIO.input(firesensor)
    print " fire  STATUS " +str(fire)
    result = instance.read()
    if result.is_valid():
        temperature = result.temperature
        humidity = result.humidity
        print temperature
        print humidity
    else:
        print "no data from sensor"
        temperature = 33
        humidity = 44
    url2 = base_url + "&field1="+str(temperature)+"&field2="+str(humidity)+"&field3="+str(0)+"&field4="+str(gas)+"&field5="+str(current_state)
    print(url2)
    f = urllib2.urlopen(url2)
    print f.read()
    f.close()
    
def camera():
    count =1
    
    current_state = GPIO.input(Doorbell)
    current_state1 = GPIO.input(pir)
    print " button state = " + str(current_state)
    print " pir state = " + str(current_state1)
    if current_state == 0 or current_state1 ==1:
        cap = cv2.VideoCapture(0)
        
        ret, frame = cap.read()
        print "Saving Photo"
        picname = datetime.now().strftime("%y-%m-%d-%H-%M")
        picname = picname+str(count)+'.jpg'
        cv2.imwrite(picname, frame)

        
        url1 = 'http://smartsecurity.thesmartbridge.com/API/image_upload/71486723251'
        files = {'fileToUpload': open(picname, 'rb')}
        r = requests.post(url1, files=files)
        print r.text
        time.sleep(5)
        cap.release()
        count=count+1

    


while True:
    previous_state = current_state
    sensors()
    camera()
    time.sleep(2)
    doorcontrol()
    #upload()
    



    

        

    
