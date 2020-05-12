from datetime import datetime
import sys
import logging as log
import cv2 as cv
import numpy as np
from collections import namedtuple
from matplotlib import pyplot as plt
from PIL import Image

class JotTable:
    def __init__(self):
        self.t_table = []
        self.t_rect = []
        self.th_hold = 3.0
        self.t_pic = []
        
    #####func comment

    def check_jot(self, tracked_objects, frames):

        cur_time = datetime.now()
        for i, tracks in enumerate(tracked_objects):
            
            for x, track in enumerate(tracks):
                _id_ = int(track.label.split()[1])

                if(len(self.t_table) <= _id_):

                    # t_table 에 초기화함수
                    # t_rext 초기화 함수
                    _len_ = len(self.t_table)
                    for _ in range(_id_ - _len_ + 1):
                        self.t_table.append([-1,-1,-1,-1,-1]) 
                        self.t_rect.append([-1,-1,-1,-1])
                        self.t_pic.append([])

                if( self.t_table[_id_][0] == -1 and self.t_table[_id_][1] == -1):
                    self.t_table[_id_] = [_id_, i, 0, 0, 0]

                if(self.t_table[_id_][2] == 0 ): # 처음 들어온 시간
                    
                    self.t_table[_id_][2] = cur_time
                    t_left, t_top, t_right, t_bottom = track.rect
                    self.t_pic[_id_] = frames[i][t_top:t_bottom, t_left:t_right]

                
                
                self.t_table[_id_][3] = cur_time #마지막 등장시간 업데이트 계속 영원히 쭉


        for i in range(len(self.t_table)): # [3]이 멈추어도 [4]는 업데이트 해서 나온애인지 판별하기 위해 시간 계속 추가해줌
            self.t_table[i][4] = cur_time
        
        # send 위한 브루트포스 시작
        for i in range(len(self.t_table)):
            if (self.t_table[i][3] != self.t_table[i][4] and self.t_table[i][3] != -1):
                # 보낼것 저장하는 리스트
                send_table = [self.t_table[i][0], self.t_table[i][1], self.t_table[i][2], self.t_table[i][3]]
                self.t_table[i] = [-1,-1,-1,-1,-1] # if 통과 못하게 초기화 시킴

                
                temp_t_1 = float(str(send_table[2]).split(':')[2])
                temp_t_2 = float(str(send_table[3]).split(':')[2])
                print((temp_t_2 - temp_t_1))
                if(temp_t_2 - temp_t_1 >= self.th_hold):
                    print("ID "+ str(send_table[0]) + " are detected!!!")
                    #sys.log("ID "+ str(send_table[0]) + "are detected!!!")
                    self.send_to_srv(send_table,frames)
                else:
                    print("ID "+ str(send_table[0]) + " are exist too small time")
                    #sys.log("ID "+ str(send_table[0]) + "are exist too small time")
                    
    
    def send_to_srv(self, send_table, frames):
        t_id = send_table[0]
        t_cam_id = send_table[1]
        print("ID : ",t_id)
        print("CAM ID : ", t_cam_id)
        print("start time : ", send_table[2])
        print("end time : ", send_table[3])

        # showup 용 추후 보내는것 추가구현 필요
        cv.imshow("detected ID : "+str(t_id), self.t_pic[t_id])



  

                

                



                





        
