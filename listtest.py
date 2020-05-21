import numpy as np
import json
from collections import OrderedDict
import codecs

#from sct import ClusterFeature, THE_BIGGEST_DISTANCE
from mc_tracker.sct import ClusterFeature, clusters_distance

#20200521 mct 에서 콜하는 클래스 확인용임.
class ListTest:
    def __init__(self):
        self.filepath = "log.json"
        self.obj_text = codecs.open(self.filepath, 'r', encoding='utf-8').read()
        self.json_load = json.loads(self.obj_text)
        self.avg_restored = np.array(self.json_load['avg_feature'], dtype=np.float32)
        self.p_id_restored = int(self.json_load['id'])
        self.cam_id_restored = int(self.json_load['cam_id'])
        self.features_restored = np.array(self.json_load['features'], dtype=np.float32)
        self.f_cluster_restored = ClusterFeature(4, self.features_restored)
        self.flag = True


    def make_restore(self):
        restored_tracks = {'id': self.p_id_restored,
                    'cam_id':  self.cam_id_restored,
                    'avg_feature': self.avg_restored,
                    'features': self.features_restored,
                    #'f_cluster': f_cluster_restored
                    'f_cluster': self.f_cluster_restored}

    def chk(self, first_cluster, second_cluster):

        print(first_cluster)
        print(second_cluster)
        
        #print(type(self.f_cluster_restored.get_clusters_matrix()))
        #print(type(origin_cluster.get_clusters_matrix()))

        if(np.array_equal(first_cluster.get_clusters_matrix(), second_cluster)):
            print("True")
        else:
            print("False")


        """
        if (self.f_cluster_restored.get_clusters_matrix() == origin_cluster.get_clusters_matrix()):
            print("ture")
        else:
            print("false")
        """








