#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 16 14:50:50 2019
This script controls the Stimul 1340 infrared laser remotely. 
It is meant as a first test script to make sure everything works correctly. 
Don't forget your goggles. 
@author: Leyla Loued-Khenissi
lkhenissi@gmail.com
ToPLab, University of Geneva
"""
import serial as serial
import time
from random import randint
import numpy as np
from datetime import datetime
from serial_ports import serial_ports
import winsound


#El En receives stuff in code
#eg for laser pulse duration, code is x ms -1; so for 4 ms, it should be 3
#Then the code for energy is ix([0.5:0.25:2]== xJ; for instance 0.5 J == 1
#watch out for 0 indexing if in python
#Then the spot size is the the size in mm -4; so for 4 mm, it is 0. 

LaserFootPulse = 4; # duration, in ms
LaserFootSpotsize =6 ; # mm, diameter
LaserFootPulseCode = LaserFootPulse - 1;
LaserFootSpotsizeCode = LaserFootSpotsize - 4;
#  The following values are in joules, estimates and should be treated with caution

high = 1.5
medium =  1.25
low = 1
thresh = 0.75

pain =[]
thisPort = serial_ports()

ser = serial.Serial(thisPort[0])  # open first serial port
print(ser.name)       # check which port was really used
ser.baudrate = 9600 #set baudrate to 9600 as in Manual p.47
ser.flush()

#The serial connection commands still need some work. Advise against running 
#Best say 0, and run the separate function instead

switchSerial = input('Serial connection open on laser (1/0)?')
if switchSerial == '1':
    t0=time.time()
    while time.time() -t0 <20:
        ser.write(b'P')
        print('Connect to serial...')
        time.sleep(0.1)
        outIt =ser.read(6)
        print(list(outIt))
else:
    pass
    
#Now for some translating into uint8
#Laser on, L111
L1 = [204, 76, 49, 49, 49, 185]
#Diode on, H111
D1 = [204, 72, 49, 49, 49, 185]
#Operate on, O111
O1 = [204, 79, 49, 49, 49, 185]

#FIRE
G1 = [204, 71, 49, 49, 49, 185]



#Laser on, L111
L0 = [204, 76, 48, 48, 48, 185]
#Diode on, H111
D0 = [204, 72, 48, 48, 48, 185]
#Operate on, O111
O0 = [204, 79, 48, 48, 48, 185]

laserLit=[]
diodeOn = []
operateOn=[]

startThis = input('Start laser (1/0)?')
if startThis == '1':
    while 'L111' not in str(laserLit):
        t0=time.time()
        ser.write(L1)
        time.sleep(0.1)
        laserLit =ser.read(6)
        print(list(laserLit))
        if 'L111' in str(laserLit):
            t1=time.time() - t0
            laserLit =ser.read(6)
            print(list(laserLit))
            print('Laser on...')
            break 
               
    time.sleep(1)
    t3=time.time() - t0
    ser.write(D1)
    time.sleep(0.1)
    diodeOn=ser.read(6)
    t4=time.time() - t0   
    print(list(diodeOn))
    if 'H111' in str(diodeOn):
        print('Diode on...')
    time.sleep(1)
    
    
    #O111 means the operate is ON state, that is the letter O, not zero
    t5=time.time() - t0
    ser.write(O1)
    time.sleep(0.1)
    operateOn = ser.read(6)
    print(list(operateOn))
    if 'O111' in str(operateOn):
        print('\n Operate on...')
    t6=time.time() - t0
            
    #all three checks must be on for system to fire$
#Now you can run the following process a few times to set your system, on laser
#test paper or in vivo. 
       
for i in range(1,10):
    print('Trial ' + str(i))
    tStart = time.time()
    pain =int(input('How much pain would you like? '))
    print(pain)
    if pain == 4 or pain > 4:
        LaserFootEnergy = high;
    elif pain == 3:
        LaserFootEnergy = medium;
    elif pain == 2:
        LaserFootEnergy = low;
    elif pain == 1:
        LaserFootEnergy = thresh;
    
    LaserFootEnergyCode = int((LaserFootEnergy/0.25)-1);
    
    if pain > 0:
     #C is to calibrate, followed by pulse parameter d (1ms * d +1), and e, energy (which is the c parameter of the P command, from 1 to 59)
        timeCalS = time.time() - tStart
        calSTR = [204, 67, LaserFootPulseCode,  LaserFootEnergyCode,  1, 185]
        ser.write(calSTR)
        resp = []
        time.sleep(0.1)
        resp = ser.read(6)
        calDone = [204, 86, LaserFootEnergyCode, 63, 63, 185]
        while 'V' not in str(resp):
            resp = ser.read(6)
            print(list(resp))
            print(chr(resp[1]), chr(resp[2]), chr(resp[3]), chr(resp[4]))
            print('\n Calibrating...')
            if 'V' in str(resp):
                print(('\n Calibrated.'))
                timeCalE = time.time() - tStart
                durCal = timeCalE - timeCalS
                time.sleep(1)   
                #P, set parameters {abc}, pulse parameter (1ms * (a + 1)), energy parameter b, (0.25 * (b +1)), spot size c in mm (diameter)
        pStr = [204, 80, LaserFootPulseCode, LaserFootEnergyCode, LaserFootSpotsizeCode, 185]
        resp2 = []
        ser.write(pStr)
        timeP = time.time() - tStart
        time.sleep(0.1)
        resp2 = ser.read(6)     
        while 'P'not in str(resp2):
            ser.write(pStr)
            time.sleep(0.1)
            resp2 = ser.read(6)
            print('\n Setting Parameters...')
            print(list(resp))
        if 'P' in str(resp2):
            print("Parameters set")
            timePSet = time.time() - tStart
            time.sleep(1)
            print('Press the laser foot pedal NOW !!!!!!\n')
            winsound.Beep(1000, 100)
            timeFP = time.time() - tStart
            time.sleep(3)
                        #Now G is the most relevant. It is th1e pain delivery
            print('\n FIRE.')
            ser.write(G1)
            time.sleep(0.1)
            resp3 = ser.read(6)
            print(list(resp3)) 
            if 'G111' in str(resp3):
                print('Laser pulse sent.')
                timeFire = time.time() - tStart
                print('Release Laser Foot Pedal NOW!\n');
            else:
                print('NO PULSE')
                time.sleep(1)
                
    elif pain == 0 or pain > 0:
        break
            #ser.flush()    
    ser.flush()
    time.sleep(3)
        
    #O000 means the operate is OFF state, that is the letter O, not zero
ser.write(O0)
time.sleep(1)
    #H000 means the diode is OFF state
ser.write(D0)
time.sleep(1)
       
     #L000 means the laser is OFF state
ser.write(L0)
time.sleep(1)

ser.close()