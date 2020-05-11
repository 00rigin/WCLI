from datetime import datetime
import logging as log
import cv2 as cv
import numpy as np
from collections import namedtuple
#from comm.comsvr import Communication

class JotTable:
    def __init__(self):
        self.t_table = []
        self.t_rect = []
        self.th_hold = 3.0
        
    #####func comment

    def check_jot(self, tracked_objects, frames):
        #log.info(tracked_objects)
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
                    """    
                    print("****************************")
                    print("t_table : ",end ='')
                    print(self.t_table)
                    print("t_rect : ", end ='')
                    print(self.t_rect)
                    """
                
                if( self.t_table[_id_][0] == -1 and self.t_table[_id_][1] == -1):
                    self.t_table[_id_] = [_id_, i, 0, 0, 0]
                """
                print("###########################")
                print("after t_table : ", end = '')
                print(self.t_table)
                """
                if(self.t_table[_id_][2] == 0 ): # 처음 들어온 시간
                    self.t_table[_id_][2] = cur_time
                    self.t_rect[_id_] = track.rect
                
                self.t_table[_id_][3] = cur_time #마지막 등장시간 업데이트 계속 영원히 쭉
            
                """
                print(_id_)
                print(self.t_table)
                """
        
        # send 위한 브루트포스 시작, 다시짜짜짜짜짜짜
        for i in range(len(self.t_table)):
            if(self.t_table[i][4] == 0):
                print("################")
                self.t_table[i][4] = cur_time
            if(self.t_table[i][3] != self.t_table[i][4]):
                _sub_ = self.t_table[i][3]-self.t_table[i][4]
                print(_sub_)
                """
                temp_t_1 = float(str(self.t_table[i][3]).split(':')[2])
                temp_t_2 = float(str(self.t_table[i][4]).split(':')[2])
                print((temp_t_2 - temp_t_1))
                if(temp_t_2 - temp_t_1 >= self.th_hold):
                    #print("chk")
                    self.send_to_srv(i ,frames)
                    
    
    def send_to_srv(self, tar_id, frame):
        print(type(tar_id))
        
        #t_left, t_top, t_right, t_bottom = self.t_rect[tar_id]
        #print(t_left, t_top, t_right, t_bottom)
        
        #dst = frame.copy()
        #dst = frame[t_top:t_bottom, t_left:t_right]
        #cv.imshow("rerererererer", dst)
        #cv.waitKey(0)
        #cv.destroyAllWindows()
        #left, top, right, bottom = obj.rect
        """
  

                

                



                





        
