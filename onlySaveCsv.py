import serial
import math
import pandas as pd
import numpy as np
from scipy import stats
from collections import deque
import time
import csv
from datetime import datetime
import atexit
from typing import NamedTuple

import threading

def calculate_acceleration_magnitude(acc_x, acc_y, acc_z):
    return math.sqrt(acc_x**2 + acc_y**2 + acc_z**2)

def calculate_force(acc_all):
    return (acc_all * G * M)

def save_val(words, data_index, id):
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

    gyr_x_key = 'gyr_x'
    gyr_y_key = 'gyr_y'
    gyr_z_key = 'gyr_z'
    acc_x_key = 'acc_x'
    acc_y_key = 'acc_y'
    acc_z_key = 'acc_z'
    acc_all_key = 'acc_all'
    force_key = 'force'

    with lock:
        data_key = f'100-{id}'
        data[data_key][gyr_x_key] = np.append(data[data_key][gyr_x_key], float(roll_r))
        data[data_key][gyr_y_key] = np.append(data[data_key][gyr_y_key], float(pitch_r))
        data[data_key][gyr_z_key] = np.append(data[data_key][gyr_z_key], float(yaw_r))
        data[data_key][acc_x_key] = np.append(data[data_key][acc_x_key], float(acc_x))
        data[data_key][acc_y_key] = np.append(data[data_key][acc_y_key], float(acc_y))
        data[data_key][acc_z_key] = np.append(data[data_key][acc_z_key], float(acc_z))
        data[data_key][acc_all_key] = np.append(data[data_key][acc_all_key], float(acc_all))
        data[data_key][force_key] = np.append(data[data_key][force_key], float(force))
                # Append to csv file
        now = datetime.now()
        date_time = now.strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"data/{date_time}_{data_key}.csv"
        with open(filename, 'a', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow([len(data[data_key][gyr_x_key]), roll_r, pitch_r, yaw_r, acc_x, acc_y, acc_z, acc_all, force])

def read_sensors():
    global data
    global lock
    while True:
        line = ser.readline()
        line = line.decode("ISO-8859-1")# .encode("utf-8")
        words = line.split(",")    # Fields split
        if(-1 < words[0].find('*')) :
            data_from=1     # sensor data
            data_index=0
            text = "ID:"+'*'
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
                        with lock:
                            save_val(words, data_index, 0)
                    if(text == "ID:100-1"):
                        with lock:
                            save_val(words, data_index, 1)
                    if (text == "ID:100-2"):
                        with lock:
                            save_val(words, data_index, 2)
                    if (text == "ID:100-3"):
                        with lock:
                            save_val(words, data_index, 3)


if __name__ == '__main__':
    M = 0.415
    G = 9.81

    ser = serial.Serial('/dev/ttyUSB0', 921600)

    lock = threading.Lock()
    cos = math.cos
    grad2rad = math.pi / 180.0
    rad2grad = 180.0 / math.pi

    class SensorData(NamedTuple):
        gyr_x: np.ndarray
        gyr_y: np.ndarray
        gyr_z: np.ndarray
        acc_x: np.ndarray
        acc_y: np.ndarray
        acc_z: np.ndarray
        acc_all: np.ndarray

    data = {}
    for i in range(5):
        data[f'100-{i}'] = np.zeros(1, dtype=[('gyr_x_'+str(i), np.float64), ('gyr_y_'+str(i), np.float64), ('gyr_z_'+str(i), np.float64), 
            ('acc_x_'+str(i), np.float64), ('acc_y_'+str(i), np.float64), ('acc_z_'+str(i), np.float64), ('acc_all'+ str(i), np.float64), ('force'+ str(i), np.float64) ])
    
    ser = serial.Serial('/dev/ttyUSB0', 921600, timeout = 0.5)

    lock = threading.Lock()

    data_thread = threading.Thread(target=read_sensors)
    data_thread.start()
    
        
