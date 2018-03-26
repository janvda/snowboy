import snowboydecoder_arecord
import sys
import signal
import paho.mqtt.client as mqtt #import the client1

interrupted = False

def signal_handler(signal, frame):
    global interrupted
    interrupted = True

def interrupt_callback():
    global interrupted
    return interrupted

"""if len(sys.argv) == 1:
    print("Error: need to specify model name")
    print("Usage: python demo.py your.model")
    sys.exit(-1)

model = sys.argv[1]"""

# capture SIGINT signal, e.g., Ctrl+C
#signal.signal(signal.SIGINT, signal_handler)

# JVA 2018-01-25 MQTT stuff
def on_message(client, userdata, message):
  global interrupted
  print("message received " ,str(message.payload.decode("utf-8")))
  print("message topic=",message.topic)
  print("message qos=",message.qos)
  print("message retain flag=",message.retain)
  cmd = str(message.payload.decode("utf-8"))
  if cmd == "status" :
    mqtt_client.publish("pi3/aiy/snowboy/status", "interrupted" if interrupted else "listening" )
  if cmd == "interrupt" :
    interrupted = True
  if cmd == "listen" :
    interrupted = False
  print ("interrupted=", interrupted)
		
global mqtt_client
mqtt_broker_address="192.168.1.131" 
mqtt_client = mqtt.Client("pi3_aiy_snowboy") #create new instance
mqtt_client.on_message = on_message
mqtt_client.connect(mqtt_broker_address) #connect to broker
mqtt_client.subscribe("pi3/aiy/snowboy/cmd",1)
mqtt_client.loop_start()

# capture SIGINT signal, e.g., Ctrl+C
#signal.signal(signal.SIGINT, signal_handler)


models = [ "./resources/models/snowboy.umdl", 
           "./resources/models/stemija.pmdl" ]
sensitivity = [0.5]*len(models)
detector = snowboydecoder_arecord.HotwordDetector(models, sensitivity=sensitivity)


# main loop
print('Listening... Press Ctrl+C to exit')
def hotword_detected():
    """
    """
    mqtt_client.publish("pi3/aiy/snowboy/event_type","hotword_detected" )
    print("hotword_detected")
		
callbacks = [lambda: hotword_detected(),
             lambda: hotword_detected()]
detector.start(detected_callback=callbacks,
               interrupt_check=interrupt_callback,
               sleep_time=0.03)

detector.terminate()
