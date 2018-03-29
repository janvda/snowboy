##################################################################################
#  logging settings  (must be put first otherwise becomes overwritten by other modules
#  
import logging

# basicConfig must be done first as otherwise becomes overwritten by other imported modules
logging.basicConfig(format='[%(asctime)s %(threadName)s, %(levelname)s] %(message)s',
                    level=logging.DEBUG)
										
logging.info('Starting program...')

####################################################################################
import snowboydecoder_arecord
import sys

import paho.mqtt.client as mqtt #import the client1

####################################################################################
#  interrupted block

import signal
interrupted = False

def signal_handler(signal, frame):
    global interrupted
    interrupted = True

def interrupt_callback():
    global interrupted
    return interrupted
		
#####################################################################################
#    MQTT stuff

def on_mqtt_message(client, userdata, message):
  global interrupted
  cmd = str(message.payload.decode("utf-8"))
  logging.info("mqtt rcvd=" + cmd + "[topic=" + message.topic + ",qos=" + str(message.qos) + ",retain=" + str(message.retain) + "]")
  if cmd == "stop" :
    interrupted = True
  elif cmd == "start" :
    interrupted = False
  elif cmd != "get_status" :
    logging.error("unexpected mqtt command (=" + cmd + ") received.  This command is not supported")
    return
  mqtt_client.publish("pi3/aiy/snowboy/status", "stopped" if interrupted else "started" )	
  logging.debug ("interrupted="+str(interrupted))
		
global mqtt_client
mqtt_broker_address="192.168.1.131" 
mqtt_client = mqtt.Client("pi3_aiy_snowboy") #create new instance
mqtt_client.on_message = on_mqtt_message
mqtt_client.connect(mqtt_broker_address) #connect to broker
mqtt_client.subscribe("pi3/aiy/snowboy/cmd",1)
mqtt_client.loop_start()

#####################################################################################
#    Snowboy stuff 
#       - specifying models, sensitivy and callback functions
#
models = [ "./resources/models/snowboy.umdl", 
           "./resources/models/stemija.pmdl" ]
sensitivity = [0.5]*len(models)
detector = snowboydecoder_arecord.HotwordDetector(models, sensitivity=sensitivity)

def hotword_detected():
    logging.info('hotword_detected')
    mqtt_client.publish("pi3/aiy/snowboy/event_type","hotword_detected" )

		
callbacks = [lambda: hotword_detected(),
             lambda: hotword_detected()]
						 
logging.info('Starting main loop ...')						 
detector.start(detected_callback=callbacks,
               interrupt_check=interrupt_callback,
               sleep_time=0.03)

logging.info('Terminating program ...')
detector.terminate()
logging.info('Program terminated.')
