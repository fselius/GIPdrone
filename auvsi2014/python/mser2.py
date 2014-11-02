#!/usr/bin/python

import cv2
import datetime
import glob
import math
import MySQLdb
import auvsiDB
from time import time

img_prefix = ""
ext = "jpg"
img_dir = "//var//www//images//"
crop_prefix = "crop_"
crop_ext = "jpg"
crop_dir = "//var//www//crops//"

host = "localhost"
user = "openCV"
passwd = "rK8sFzmWVFJ4CMm5"
dbname = "openCV"


def get_target(arr):
    X = int(arr[:,0].max() + arr[:,0].min())/2
    Y = int(arr[:,1].max() + arr[:,1].min())/2
    D = max((arr[:,0].max() - arr[:,0].min()), (arr[:,1].max() - arr[:,1].min()))
    
    return (X,Y,D)

def processImage(img, altitude, lon, lat, groll, gpitch, gyaw, resize_factor = 4, isActive = False, hsv_channel = 0, mser_params = {'_delta' : 5, '_min_area' : 60, '_max_area' : 14400, '_max_variation' : 0.25, '_min_diversity' : 0.2, '_max_evolution' : 200, '_area_threshold' : 1.01, '_min_margin' : 0.003, '_edge_blur_size' : 5}):
    # Runs mser on input image, stores results to DB
    debug = False
    starttime = time()
    try:
        frame = cv2.imread(img, cv2.CV_LOAD_IMAGE_COLOR)
        vis = frame.copy()
    except Exception as e:
        print e
        return 0
    
    start = datetime.datetime.now()
    db = MySQLdb.connect(host = auvsiDB.host, user = auvsiDB.user, passwd = auvsiDB.passwd, db = auvsiDB.db)
    cur = db.cursor()
    
    # Get image ID from the DB
    sql = "INSERT INTO `{}`.`images` (`id`, `time`, `milisec`, `alt`, `lon`, `lat`, `groll`, `gpitch`, `gyaw`, `src`, `sent`)".format(auvsiDB.db)
    sql = sql + "VALUES (NULL, '{}',  MICROSECOND('{}'), '{}', '{}', '{}', '{}', '{}', '{}', '', 'false');".format(str(start), str(start), altitude, lon, lat, groll, gpitch, gyaw)
    cur.execute(sql)
    iidx = cur.lastrowid
	
    # Creates a new frame to be resized and sent to the ground
    
    shape = (frame.shape[1]/resize_factor, frame.shape[0]/resize_factor)
    vis = cv2.resize(vis, shape)
    cv2.imwrite("{}{}{}.{}".format(img_dir, img_prefix, iidx, ext), vis)
    
    # Converts image to HSV, process MSER on a single channel
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mser_channel = hsv[:,:,hsv_channel]
    
    # Runs MSER if isActive is set to true, otherwise resize and sends the picture
    areas = list()
    if isActive == True:
        mser = cv2.MSER(**mser_params)
        areas = mser.detect(mser_channel)

    targets = list()
    
    # Creates a copy of the image to draw areas created by MSER
    if debug == True:
        tmpframe = frame.copy()
        hulls = [cv2.convexHull(p.reshape(-1, 1, 2)) for p in areas]
        cv2.polylines(tmpframe, hulls, 1, (0, 255, 0), thickness=1)
    
    # Combines close targets to rectangles
    for p in areas:
        if len(targets) == 0:
            targets.append([p[:,0].max(), p[:,0].min(), p[:,1].max(), p[:,1].min()])
        for t,__ignore in enumerate(targets):
            dx = abs(targets[t][0]-targets[t][1])
            dy = abs(targets[t][2]-targets[t][3])
            rat = 0.0
            # If the area intersects with an existing target rectangle they are joined 
            if p[:,0].max() > (targets[t][1] - dx*rat) and p[:,0].min() < (targets[t][0] + dx*rat) and p[:,1].max() > (targets[t][3] - dy*rat) and p[:,1].min() < (targets[t][2] + dy*rat):
                if p[:,0].max() > targets[t][0]:targets[t][0] = p[:,0].max()
                if p[:,0].min() < targets[t][1]:targets[t][1] = p[:,0].min()
                if p[:,1].max() > targets[t][2]:targets[t][2] = p[:,1].max()
                if p[:,1].min() < targets[t][3]:targets[t][3] = p[:,1].min()
                break
        else:
            targets.append([p[:,0].max(), p[:,0].min(), p[:,1].max(), p[:,1].min()])

    # Creates squares crops from the targets found
    for idx, t in enumerate(targets):
        x_min = t[1]
        x_max = t[0]
        y_min = t[3]
        y_max = t[2]
        
        rad = max(x_max-x_min, y_max-y_min)*0.5
        x_min = max(int((x_max + x_min)/2.0 - rad*1.5), 0)
        y_min = max(int((y_max + y_min)/2.0 - rad*1.5), 0)
        x_max = min(int(x_min + rad*3), frame.shape[1])
        y_max = min(int(y_min + rad*3), frame.shape[0])
        
        if debug == True:
            cv2.rectangle(tmpframe, (x_min, y_min), (x_max, y_max), (0, 255, 255), thickness=2)
        
        crop = frame[y_min:y_max, x_min:x_max,:].copy()
        cv2.imwrite("{}{}{}_{}.{}".format(crop_dir, crop_prefix, iidx, idx, crop_ext), crop)
        sql = "INSERT INTO `{}`.`crops` (`fatherid`, `id`, `c1x`, `c1y`, `c2x`, `c2y`, `c3x`, `c3y`, `c4x`, `c4y`) VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}');".format(auvsiDB.db, iidx, idx, x_min, y_min, x_max, y_min, x_max, y_max, x_min, y_max)
        cur.execute(sql)
        
    if debug == True:    
        tmpframe = cv2.resize(tmpframe, shape)
        cv2.imwrite("{}{}{}.{}".format(img_dir, "mser_"+img_prefix, iidx, ext), tmpframe)

    db.commit()	
    cur.close()
    db.close()
    print "Ended: \t\t",img, "\t\ttook: ", time()-starttime

if __name__ == '__main__':

	images = glob.glob('/home/odroid/opencv/4mp_pics/tmp/*.JPG')
	prog_init = datetime.datetime.now()
	#for img in images:
	#	frame = cv2.imread(img, cv2.CV_LOAD_IMAGE_COLOR)
	#	processImage(frame, 500.5, 35.555, 34.4444, 0.1, 0.2, 0.3)

	k = 500
	for i in range(0,k):
		t = i%len(images)
		frame = cv2.imread(images[t], cv2.CV_LOAD_IMAGE_COLOR)
		processImage(frame, 500.5, 35.555, 34.4444, 0.1, 0.2, 0.3)
	#	print images[t]
		

	print "---------------------------"
	print "Total time: {}".format(datetime.datetime.now()-prog_init)
