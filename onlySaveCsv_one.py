import serial
import math
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib import animation
import numpy as np
from scipy import stats
from collections import deque
import time
import csv
from datetime import datetime
import atexit
from influxdb import InfluxDBClient
from typing import NamedTuple

def calculate_acceleration_magnitude(acc_x, acc_y, acc_z):
    return math.sqrt(acc_x**2 + acc_y**2 + acc_z**2)

def calculate_force(acc_all):
    return (acc_all * G * M)

def save_val(words, data_index, num):
    roll = float(words[data_index]) * grad2rad
    pitch = float(words[data_index+1]) * grad2rad
    yaw = float(words[data_index+2]) * grad2rad
    acc_x = float(words[data_index+3])
    acc_y = float(words[data_index+4])
    acc_z = float(words[data_index+5])
    roll_r = "%.2f" % (roll * rad2grad)
    pitch_r = "%.2f" % (pitch * rad2grad)
    yaw_r = "%.2f" % (yaw * rad2grad)
    acc_all = calculate_acceleration_magnitude(acc_x, acc_y, acc_z)
    force = calculate_force(acc_all)

    with open('/home/dohlee/ras_data_tmp/data/data.csv','a') as csv_file:
        csv_writer = csv.DictWriter(csv_file,fieldnames=fieldnames)
        info = {
            "Packet number": num,
            "Gyroscope X (deg/s)":roll_r,
            "Gyroscope Y (deg/s)":pitch_r,
            "Gyroscope Z (deg/s)": yaw_r,
            "Accelerometer X (g)": acc_x,
            "Accelerometer Y (g)": acc_y,
            "Accelerometer Z (g)": acc_z,
            "AccAll": acc_all,
            "Force": force
            #"Force": af
        }
        csv_writer.writerow(info)


def read_serial():
    global num
    line = ser.readline()
    line = line.decode("ISO-8859-1")
    words = line.split(",")

    if (-1 < words[0].find('*')) :
        data_from = 1
        data_index = 0
        text = "ID:" + '*'
        words[0]=words[0].replace('*','')
    else :
        if(-1 < words[0].find('-')) :
            data_from=2  # rf_receiver data
            data_index=1
            text = "ID:"+words[0]
        else :
            data_from=0  # unknown format
        if(data_from!=0):
            commoma = words[data_index].find('.') 
            if(len(words[data_index][commoma:-1])==4):
                data_format = 2  # quaternion
            else :
                data_format = 1 # euler
            if(data_format==1): #euler
                if (text == "ID:100-0"):
                    save_val(words, data_index,num)
                    num += 1

if __name__ == '__main__':
    M = 0.415
    G = 9.81
    num = 0
    cos = math.cos
    grad2rad = math.pi / 180.0
    rad2grad = 180.0 / math.pi

    ser = serial.Serial('/dev/ttyUSB0', 921600)


    s_gyr_x = deque()
    s_gyr_y = deque()
    s_gyr_z = deque()
    s_acx = deque()
    s_acy = deque()
    s_acz = deque()


    fieldnames = ["Packet number", "Gyroscope X (deg/s)","Gyroscope Y (deg/s)", "Gyroscope Z (deg/s)", "Accelerometer X (g)", "Accelerometer Y (g)", "Accelerometer Z (g)", "AccAll", "Force"]

    with open('data/data.csv','w') as csv_file:
        csv_writer = csv.DictWriter(csv_file, fieldnames = fieldnames)
        csv_writer.writeheader()
    while(1):
        read_serial()
