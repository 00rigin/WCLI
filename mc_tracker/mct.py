
import queue

import numpy as np
from scipy.spatial.distance import cosine

from .sct import SingleCameraTracker, clusters_distance, THE_BIGGEST_DISTANCE

# for jason
import json
from collections import OrderedDict
import codecs
#추가함
from encoder import NumpyEncoder



class MultiCameraTracker:
    def __init__(self, num_sources, reid_model,
                 sct_config={},
                 time_window=20,
                 global_match_thresh=0.35
                 ):
        self.scts = []
        self.time = 0
        self.last_global_id = 0
        self.global_ids_queue = queue.Queue()
        self.time_window = time_window  # should be greater than time window in scts
        self.global_match_thresh = global_match_thresh
        for i in range(num_sources):
            self.scts.append(SingleCameraTracker(i, self._get_next_global_id,
                                                 self._release_global_id,
                                                 reid_model, **sct_config))

    def make_file(self, tracks):
        file_data = OrderedDict()
        #file_data = tracks
        #print(json.dumps(file_data, ensure_ascii=False, indent="\t"))
        #print(type(tracks[0]['features'][0]))
        
        for track in tracks:
    
            #file_data['id'] = track['id']
            file_data['id'] = "target"
            file_data['cam_id'] = track['cam_id']
            file_data['avg_feature'] = track['avg_feature'].tolist()
            file_data['f_cluster'] = str(track['f_cluster'])
            file_data['features'] = []
            for obj in (track['features']):
                file_data['features'].append(obj.tolist())    
            
            with open('./log.json', 'w', encoding="utf-8") as make_file: 
                json.dump(file_data, make_file, ensure_ascii=False, indent='\t')


    def process(self, frames, all_detections, masks=None):
        assert len(frames) == len(all_detections) == len(self.scts)
        all_tracks = []
        for i, sct in enumerate(self.scts):
            if masks:
                mask = masks[i]
            else:
                mask = None
            sct.process(frames[i], all_detections[i], mask)

            """
            sct.get_tracks() : 하면 tuple 형식으로 id 와 좌표, 피쳐값 저장됨.
            """
            
            all_tracks += sct.get_tracks()
            

            """       
            print("*******************************")
            print(type(all_tracks))
            """
            """
            f = open("./log.txt", 'w')
            f.write(str(all_tracks))
            #while(True): a = 1
            """
        # for make json file
        print(all_tracks)
        return all_tracks
            

        if self.time > 0 and self.time % self.time_window == 0:
            distance_matrix = self._compute_mct_distance_matrix(all_tracks)
            assignment = self._compute_greedy_assignment(distance_matrix)

            for i, idx in enumerate(assignment):
                if idx is not None and all_tracks[idx]['id'] is not None and all_tracks[i]['timestamps'] is not None:
                    if all_tracks[idx]['id'] >= all_tracks[i]['id']:
                        if all_tracks[idx]['timestamps'][0] >= all_tracks[i]['timestamps'][0]:
                            self.scts[all_tracks[idx]['cam_id']].check_and_merge(all_tracks[i], all_tracks[idx])
                    else:
                        if all_tracks[idx]['timestamps'][0] <= all_tracks[i]['timestamps'][0]:
                            self.scts[all_tracks[i]['cam_id']].check_and_merge(all_tracks[idx], all_tracks[i])

        self.time += 1

    def _compute_mct_distance_matrix(self, all_tracks):
        distance_matrix = THE_BIGGEST_DISTANCE * np.eye(len(all_tracks), dtype=np.float32)
        for i, track1 in enumerate(all_tracks):
            for j, track2 in enumerate(all_tracks):
                if j >= i:
                    break
                if track1['id'] != track2['id'] and track1['cam_id'] != track2['cam_id'] and \
                        len(track1['timestamps']) > self.time_window and len(track2['timestamps']) > self.time_window and \
                        track1['avg_feature'] is not None and track2['avg_feature'] is not None:
                    clust_dist = clusters_distance(track1['f_cluster'], track2['f_cluster'])
                    avg_dist = cosine(track1['avg_feature'], track2['avg_feature'])
                    distance_matrix[i, j] = min(clust_dist, avg_dist)
                else:
                    distance_matrix[i, j] = 10
        return distance_matrix + np.transpose(distance_matrix)

    def _compute_greedy_assignment(self, distance_matrix):
        assignment = [None]*distance_matrix.shape[0]
        indices_rows = np.arange(distance_matrix.shape[0])
        indices_cols = np.arange(distance_matrix.shape[1])

        while (len(indices_rows) > 0 and len(indices_cols) > 0):
            i, j = np.unravel_index(np.argmin(distance_matrix), distance_matrix.shape)
            dist = distance_matrix[i, j]
            if dist < self.global_match_thresh:
                assignment[indices_rows[i]] = indices_cols[j]
                distance_matrix = np.delete(distance_matrix, i, 0)
                distance_matrix = np.delete(distance_matrix, j, 1)
                indices_rows = np.delete(indices_rows, i)
                indices_cols = np.delete(indices_cols, j)
            else:
                break

        return assignment

    def _get_next_global_id(self):
        if self.global_ids_queue.empty():
            self.global_ids_queue.put(self.last_global_id)
            self.last_global_id += 1

        return self.global_ids_queue.get_nowait()

    def _release_global_id(self, id):
        assert id <= self.last_global_id
        self.global_ids_queue.put(id)

    def get_tracked_objects(self):
        
        objs = [sct.get_tracked_objects() for sct in self.scts]
        return objs

    def get_all_tracks_history(self):
        history = []
        for sct in self.scts:
            cam_tracks = sct.get_archived_tracks() + sct.get_tracks()
            for i in range(len(cam_tracks)):
                cam_tracks[i] = {'id': cam_tracks[i]['id'],
                                 'timestamps':  cam_tracks[i]['timestamps'],
                                 'boxes': cam_tracks[i]['boxes']}

            history.append(cam_tracks)

        return history
