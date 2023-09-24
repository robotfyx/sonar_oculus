#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 22 10:24:51 2023

@author: 99358
"""

import numpy as np
import cv2
from scipy.interpolate import interp1d

import rospy
import cv_bridge
from oculus_sonar.msg import Ping
from sensor_msgs.msg import Image
import message_filters

REVERSE_Z = 1
global res, height, rows, width, cols, map_x, map_y, f_bearings
res, height, rows, width, cols = None, None, None, None, None
map_x, map_y = None, None
f_bearings = None

bridge = cv_bridge.CvBridge()

to_rad = lambda bearing: bearing * np.pi / 18000

def generate_map_xy(ping):
    _res = ping.rangeResolution
    _height = ping.nRanges * _res
    _rows = ping.nRanges
    _width = np.sin(
        to_rad(ping.bearings[-1] - ping.bearings[0]) / 2) * _height * 2
    _cols = int(np.ceil(_width / _res))

    global res, height, rows, width, cols, map_x, map_y, f_bearings
    if res == _res and height == _height and rows == _rows and width == _width and cols == _cols:
        return
    res, height, rows, width, cols = _res, _height, _rows, _width, _cols

    bearings = to_rad(np.asarray(ping.bearings, dtype=np.float32))
    f_bearings = interp1d(
        bearings,
        range(len(bearings)),
        kind='cubic',
        bounds_error=False,
        fill_value=-1,
        assume_sorted=True)

    XX, YY = np.meshgrid(range(cols), range(rows))
    
    x = res * (rows - YY)
    y = res * (-cols / 2.0 + XX + 0.5)
    b = np.arctan2(y, x) * REVERSE_Z
    r = np.sqrt(np.square(x) + np.square(y))
    map_y = np.asarray(r / res, dtype=np.float32)
    map_x = np.asarray(f_bearings(b), dtype=np.float32)

def process(image):
    ret,binary = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    out = cv2.bitwise_and(image, binary)
    
    return out    

def callback(data1, data2):
    generate_map_xy(data1)

    img = bridge.imgmsg_to_cv2(data2, desired_encoding='passthrough')
    img = process(img)
    img = np.array(img, dtype=img.dtype, order='F')

    if cols > img.shape[1]:
        img.resize(rows, cols)
        
    img = cv2.remap(img, map_x, map_y, cv2.INTER_CUBIC)
    img = cv2.applyColorMap(img, 2)
    
    img_msg = bridge.cv2_to_imgmsg(img, encoding="bgr8")
    img_msg.header.stamp = rospy.Time.now()
    img_pub.publish(img_msg)
    
if __name__ == '__main__':
    rospy.init_node('oculus_viewer')
    rospy.loginfo('start!')
    img_pub = rospy.Publisher('/oculus_viewer/Image', Image, queue_size=10)
    
    sub1 = message_filters.Subscriber('/oculus_sonar/ping', Ping)#订阅相关参数
    sub2 = message_filters.Subscriber('/oculus_sonar/ping_image', Image)#订阅原始图像
    ts = message_filters.TimeSynchronizer([sub1, sub2], 10)
    ts.registerCallback(callback)
    
    rospy.spin()
