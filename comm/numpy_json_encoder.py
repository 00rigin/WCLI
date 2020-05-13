import json
from collections import OrderedDict
import numpy as np

class NumpyEncoder(json.JSONEncoder):
    def Fornp(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)



