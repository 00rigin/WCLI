import json
from collections import OrderedDict
import codecs
import numpy as np
from collections import namedtuple

class RECV:
    
    def __init__(self):
        self.pi_filepath = "pi_jot.json"
        self.obj_text = codecs.open(self.pi_filepath, 'r', encoding='utf-16').read()
        self.json_load = json.loads(self.obj_text)

        self.avg_restored = np.array(self.json_load['avg_feature'], dtype=np.float32)
        self.id_restored = int(self.json_load['id'])
        self.f_cluster_mat_restored = np.array(self.json_load['f_cluster_mat'], dtype=np.float32)


        
    
    def recov_file(self, flag):

        if(flag):

            restored_tracks = {'id': self.id_restored,
                        'avg_feature': self.avg_restored,
                        'f_cluster_mat': self.f_cluster_mat_restored}

            #print(restored_tracks)
            
            return restored_tracks
        
        else:
            return 0


        # 복구용
        """
        obj_text = codecs.open(filepath, 'r', encoding='utf-8').read()
        json_load = json.loads(obj_text)
        pic_restored = np.array(json_load['pic'], dtype=np.uint8)
        p_id_restored = int(json_load['p_id'])
        cam_id_restored = int(json_load['cam_id'])
        s_time_restored = str(json_load['start_time1'])
        e_time_restored = str(json_load['end_time1'])

        print("p_id : ", p_id_restored)
        print("cam_id : ", cam_id_restored)
        print("s_time : ", s_time_restored)
        print("e_time : ", e_time_restored)
        cv.imshow("restored", pic_restored)
        """