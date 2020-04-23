"""
 Copyright (c) 2019 Intel Corporation
 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at
      http://www.apache.org/licenses/LICENSE-2.0
 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.
"""

import sys
import os

import logging as log
import numpy as np

from openvino.inference_engine import IENetwork, IECore # pylint: disable=import-error,E0611
import cv2 as cv


class IEModel:
    """Class for inference of models in the Inference Engine format"""
    def __init__(self, exec_net, inputs_info, input_key, output_key):
        self.net = exec_net
        self.inputs_info = inputs_info
        self.input_key = input_key
        self.output_key = output_key
        self.reqs_ids = []

    def _preprocess(self, img):
        _, _, h, w = self.get_input_shape().shape
        img = np.expand_dims(cv.resize(img, (w, h)).transpose(2, 0, 1), axis=0)
        return img

    def forward(self, img):
        """Performs forward pass of the wrapped IE model"""
        res = self.net.infer(inputs={self.input_key: self._preprocess(img)})
        return np.copy(res[self.output_key])

    def forward_async(self, img):
        id = len(self.reqs_ids)
        self.net.start_async(request_id=id,
                             inputs={self.input_key: self._preprocess(img)})
        self.reqs_ids.append(id)

    def grab_all_async(self):
        outputs = []
        for id in self.reqs_ids:
            self.net.requests[id].wait(-1)
            res = self.net.requests[id].outputs[self.output_key]
            outputs.append(np.copy(res))
        self.reqs_ids = []
        return outputs

    def get_input_shape(self):
        """Returns an input shape of the wrapped IE model"""
        return self.inputs_info[self.input_key]


def load_ie_model(ie, model_xml, device, plugin_dir, cpu_extension='', num_reqs=1):
    """Loads a model in the Inference Engine format"""
    model_bin = os.path.splitext(model_xml)[0] + ".bin"
    # Plugin initialization for specified device and load extensions library if specified
    log.info("Initializing Inference Engine plugin for %s ", device)

    if cpu_extension and 'CPU' in device:
        ie.add_extension(cpu_extension, 'CPU')
    # Read IR
    log.info("Loading network files:\n\t%s\n\t%s", model_xml, model_bin)
    net = IENetwork(model=model_xml, weights=model_bin)

    if "CPU" in device:
        supported_layers = ie.query_network(net, "CPU")
        not_supported_layers = [l for l in net.layers.keys() if l not in supported_layers]
        if not_supported_layers:
            log.error("Following layers are not supported by the plugin for specified device %s:\n %s",
                      device, ', '.join(not_supported_layers))
            log.error("Please try to specify cpu extensions library path in sample's command line parameters using -l "
                      "or --cpu_extension command line argument")
            sys.exit(1)

    assert len(net.inputs.keys()) == 1 or len(net.inputs.keys()) == 2, \
        "Supports topologies with only 1 or 2 inputs"
    assert len(net.outputs) == 1 or len(net.outputs) == 5, \
    log.info("Loading network files:\n\t%s\n\t%s", model_xml, model_bin)
    net = IENetwork(model=model_xml, weights=model_bin)


    log.info("Preparing input blobs")
    input_blob = next(iter(net.inputs))
    out_blob = next(iter(net.outputs))
    net.batch_size = 1

    # Loading model to the plugin
    log.info("Loading model to the plugin")
    exec_net = ie.load_network(network=net, device_name=device, num_requests=num_reqs)
    model = IEModel(exec_net, net.inputs, input_blob, out_blob)
    return model


#######################################추가됨############################
"""
class NcsClassifier(object):
    def __init__(self, id, queue, model_xml):
        self._id = id
        self.current_request_id = 0
        self.next_request_id = 1
        self._queue = queue
        self._load_model(model_xml)

    def _load_model(self, model_xml):
        model_bin = os.path.splitext(model_xml)[0] + ".bin"

        # Plugin initialization for specified device and load extensions library if specified
        self.plugin = IEPlugin(device='MYRIAD')
        #self.plugin.set_config({"VPU_FORCE_RESET":"NO"})
        # Read IR
        log.info("Loading network files:\n\t{}\n\t{}".format(model_xml, model_bin))
        self.net = IENetwork.from_ir(model=model_xml, weights=model_bin)
        self.exec_net = self.plugin.load(network=self.net, num_requests=2)

    def predict(self, image):
        input_blob = next(iter(self.net.inputs))
        out_blob = next(iter(self.net.outputs))

        # do inference
        res = self.exec_net.infer(inputs={input_blob: image})

        # get result back
        output = res[out_blob]

        probs = np.squeeze(output[0])
        top_ind = np.argsort(probs)[-1:][::-1]
        return top_ind

    def predict_async(self, image):
        input_blob = next(iter(self.net.inputs))
        out_blob = next(iter(self.net.outputs))

        self.exec_net.start_async(request_id=self.next_request_id,
                                  inputs={input_blob: image})

        if self.exec_net.requests[self.current_request_id].wait(-1) == 0:
            res = self.exec_net.requests[self.current_request_id].outputs[out_blob]
            probs = np.squeeze(res)
            top_ind = np.argsort(probs)[-1:][::-1]
            print("Woker id {}, predicted index {}".format(self._id, top_ind))

        # exchange request id
        self.current_request_id, self.next_request_id = self.next_request_id, self.current_request_id


class Scheduler:
    def __init__(self, deviceids, model_xml):
        self._queue = queue.Queue()
        self._ids = deviceids
        self.__init_workers(model_xml)

    def __init_workers(self, model_xml):
        self._workers = list()
        for _id in self._ids:
            self._workers.append(NcsClassifier(_id, self._queue, model_xml))

    def start(self, xfilelst, input_shape):

        start_time = time()
        # start the workers
        threads = []

        n, c, h, w = input_shape

        # add producer thread for image pre-processing
        producer_thread = threading.Thread(target=image_preprocess_job, args=(self._queue, xfilelst, w, h))
        producer_thread.start()
        threads.append(producer_thread)

        # schedule workers
        for worker in self._workers:
            thworker = threading.Thread(target=inference_job_async, args=(self._queue, worker))
            thworker.start()
            threads.append(thworker)

        # wait all fo workers finish
        for _thread in threads:
            _thread.join()

        end_time = time()
        print("all of workers have been done within ", end_time - start_time)
"""