import paho.mqtt.client as mqtt
import random, threading, json
import numpy as np
from PIL import Image
import os
from datetime import datetime
import time
from imutils import opencv2matplotlib
from helper import pil_image_to_byte_array, get_now_string, get_config
import matplotlib.image as mpimg
# ====================================================
# MQTT Settings
MQTT_Broker = "192.168.0.101"
MQTT_Port = 8888
Keep_Alive_Interval = 45
MQTT_Topic = "camera/image"
path_dir = 'C:\\Users\\jacky\\Desktop\\oh_my_girl\\'
pix_path_dir = "C:\\Users\\jacky\\Desktop\\np_image\\"


# ====================================================

def on_connect(client, userdata, rc):
    if rc != 0:
        pass
        print("Unable to connect to MQTT Broker...")
    else:
        print("Connected with MQTT Broker: " + str(MQTT_Broker))


def on_publish(client, userdata, mid):
    pass


def on_disconnect(client, userdata, rc):
    if rc != 0:
        pass


def get_mqtt_client():
    client = mqtt.Client()
    client.connected_flag = False  # set flag
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_publish = on_publish
    return client

def publish_To_Topic(topic, message, client):
    client.publish(topic, message)
    print("Published: " + str(message) + " " + "on MQTT Topic: " + str(topic))
    print("")


# ====================================================
# FAKE SENSOR
# Dummy code used as Fake Sensor to publish some random values
# to MQTT Broker

#toggle = 0


def publish_Fake_Sensor_Values_to_MQTT():
    #threading.Timer(3.0, publish_Fake_Sensor_Values_to_MQTT).start()
    client = get_mqtt_client()
    client.connect(MQTT_Broker, port=MQTT_Port)
    file_list = os.listdir(path_dir)
    # pix_list = os.listdir(pix_path_dir)
    for image in file_list:
        #im = Image.open(path_dir+image)

        '''
        im = mpimg.imread(path_dir+image)
        np_array_RGB = opencv2matplotlib(im)
        image = Image.fromarray(np_array_RGB)
        byte_array = pil_image_to_byte_array(image)
        '''

        print("publishing image data in pixel data ")
        #publish_To_Topic(MQTT_Topic, byte_array, client)
        publish_To_Topic(MQTT_Topic, image, client)
        print("finish publish")




publish_Fake_Sensor_Values_to_MQTT()

# ====================================================
