from machine import Pin
import time
import dht
import ujson
from umqtt.simple import MQTTClient

# MQTT Server Parameters
MQTT_CLIENT_ID = "aaokwkwlkwwokwwwbwhhw"
MQTT_BROKER    = "broker.emqx.io"
MQTT_USER      = ""
MQTT_PASSWORD  = ""
MQTT_TOPIC     = "/UNI038/Fauzan_Arif_Tricahya/data_sensor"
MQTT_SUBS_TOPIC = "/UNI038/Fauzan_Arif_Tricahya/aktuasi_led"


led = Pin(4, Pin.OUT)

def do_connect():
    import network
    sta_if = network.WLAN(network.WLAN.IF_STA)
    if not sta_if.isconnected():
        print('connecting to network...')
        sta_if.active(True)
        sta_if.connect('POCO M3', 'Palem2f8771')
        while not sta_if.isconnected():
            pass
    print('network config:', sta_if.ipconfig('addr4'))

def sub_cb(topic, msg):
  print("You got new message ",msg)
  msg = msg.decode('utf-8')
  
  if "on" in msg.lower():
      led.on()
      print("nyalakan lampu")
  elif "off" in msg.lower():
      led.off()
      print("matikan lampu")
  else:
      print("Perintah tidak dikenal")
  


# connect to WiFi
do_connect()

#connect & subscribe to MQTT Server
print("Connecting to MQTT server... ", end="")
client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, user=MQTT_USER, password=MQTT_PASSWORD)
client.set_callback(sub_cb)
client.connect()
client.subscribe(MQTT_SUBS_TOPIC)
print("Done Connect to MQTT Server!")

sensor = dht.DHT11(Pin(5))
'''
  if the degree over 40C  -> The light turns on
  if the degree below 40C -> The light turns off
  '''
while True:
  try:
      new_message = client.check_msg()
      sensor.measure() # read the parameters from the sensor
      message = ujson.dumps({
          "temp": sensor.temperature(),
          "humidity": sensor.humidity(),
      })
      #print("Updated!")
      #print("Reporting to MQTT topic {}: {}".format(MQTT_TOPIC, message))
      client.publish(MQTT_TOPIC, message)
      time.sleep(1)
  except Exception as e:
      print(e)

