#!/usr/bin/env python

'''
Lucas-Kanade tracker
====================

We used Lucas-Kanade sparse optical flow uses goodFeaturesToTrack
for track initialization and back-tracking for match verification
between frames.
'''

import numpy as np
import cv2

def draw_str(dst, (x, y), s):
    cv2.putText(dst, s, (x+1, y+1), cv2.FONT_HERSHEY_PLAIN, 1.0, (0, 0, 0), thickness = 2, lineType=cv2.CV_AA)
    cv2.putText(dst, s, (x, y), cv2.FONT_HERSHEY_PLAIN, 1.0, (255, 255, 255), lineType=cv2.CV_AA)

lk_params = dict( winSize  = (15, 15),
                  maxLevel = 2,
                  criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))

feature_params = dict( maxCorners = 500,
                       qualityLevel = 0.6,
                       minDistance = 30,
                       blockSize = 15)

class App:
    def __init__(self, video_src,init_frame_num):
        self.track_len = 15
        self.detect_interval = 30
        self.tracks = []
        self.init_frame_num = init_frame_num
        self.cam = cv2.VideoCapture(video_src)
        self.frame_idx = init_frame_num
        
    frame_num = 1
    def run(self):
        fourcc = cv2.cv.CV_FOURCC(*'XVID')
        out = cv2.VideoWriter('OptFlowDet.avi',fourcc, 20.0, (320,240))
        
        while True:
            
            ret, frame = self.cam.read()
            if frame==None:
                break
            
            frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            vis = frame.copy()
            
            if len(self.tracks) > 0:
                img0, img1 = self.prev_gray, frame_gray
                p0 = np.float32([tr[-1] for tr in self.tracks]).reshape(-1, 1, 2)
                p1, st, err = cv2.calcOpticalFlowPyrLK(img0, img1, p0, None, **lk_params)
                p0r, st, err = cv2.calcOpticalFlowPyrLK(img1, img0, p1, None, **lk_params)
                #back projecting of next frame to the previous to find good match                
                d = abs(p0-p0r).reshape(-1, 2).max(-1)
                good = d < 1
                new_tracks = []
                for tr, (x, y), good_flag in zip(self.tracks, p1.reshape(-1, 2), good):
                    if not good_flag:
                        continue
                    tr.append((x, y))
                    if len(tr) > self.track_len:
                        del tr[0]
                    new_tracks.append(tr)
                    cv2.circle(vis, (x, y), 2, (0, 255, 0), -1)
                self.tracks = new_tracks
                
                con_p1 = cv2.convexHull(np.int32(self.tracks[1]), returnPoints=True)                
                            
                #find initial bounding box
                x,y,w,h = cv2.boundingRect(con_p1)
                init = open("C:\\Users\\NoaMyara\\Documents\\MATLAB\\DroneProject\\OpenTLD-master\\_input_noa\\init.txt","w")
                init.writelines('{}, {}, {}, {}'.format(x-12,y-12,x+12,y+12))
                frame_num = open("C:\\Users\\NoaMyara\\Documents\\MATLAB\\DroneProject\\OpenTLD-master\\_input_noa\\frame_num.txt","w")
                frame_num.writelines('{}'.format(self.frame_idx))
                frame_num.close()
                
                if self.frame_idx >= self.init_frame_num:
                    break
                
                cv2.polylines(vis, [np.int32(tr) for tr in self.tracks], False, (0, 255, 0))
                draw_str(vis, (20, 20), 'track count: %d' % len(self.tracks))
                
            if self.frame_idx % self.detect_interval == 0:
                mask = np.zeros_like(frame_gray)
                mask[:] = 255
                for x, y in [np.int32(tr[-1]) for tr in self.tracks]:
                    cv2.circle(mask, (x, y), 5, 0, -1)
                p = cv2.goodFeaturesToTrack(frame_gray, mask = mask, **feature_params)
                if p is not None:
                    for x, y in np.float32(p).reshape(-1, 2):
                        self.tracks.append([(x, y)])
                        
            


            self.frame_idx += 1
            self.prev_gray = frame_gray
            
            #out.write(vis)
            ch = 0xFF & cv2.waitKey(1)
            if ch == 27:
                break
        out.release()  

def main():
    import sys
    try: video_src = sys.argv[1]
    except: video_src = 0
    
     
    init_frame_num = int(sys.argv[2])
    print(type(init_frame_num))
    App(video_src,init_frame_num).run()
    cv2.destroyAllWindows()
    
if __name__ == '__main__':
    main()
