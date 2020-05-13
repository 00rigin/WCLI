from helper import  byte_array_to_pil_image, get_now_string, get_config
import paho.mqtt.client as mqtt
import time
from mqtt import get_mqtt_client
import cv2
import matplotlib.pyplot as pp

# MQTT Settings
MQTT_Broker = "127.0.0.1"
MQTT_Port = 8282
Keep_Alive_Interval = 45
MQTT_Topic = "camera/image"
save_dir = 'C:\\Users\\worl6\\Desktop\\mqttSave\\'
#Subscribe to all Sensors at Base Topic

#Save Data into DB Table
def on_message(mosq, obj, msg):
    print("MQTT Data Received...")
    print("MQTT Topic: " + msg.topic)
   # now = get_now_string()
   # print("message on " + str(msg.topic) + f" at {now}")
    try:

        print(msg)
        image = byte_array_to_pil_image(msg.payload)
        image = image.convert("RGB")
       # save_file_path = save_dir + f"capture_{now}.jpg"

        pp.imshow(image)
        pp.show()


    # cv2.imwrite(save_file_path, image)
       # print(f"Saved {save_file_path}")

    except Exception as exc:
        print(exc)
    print(type(msg.payload))



def main():
    client = get_mqtt_client()
    client.on_message = on_message
    client.connect(MQTT_Broker, port=MQTT_Port)
    client.subscribe(MQTT_Topic)
    time.sleep(4)  # Wait for connection setup to complete
    client.loop_forever()


if __name__ == "__main__":
    main()


