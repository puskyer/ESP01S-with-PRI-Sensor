# Complete project details at https://RandomNerdTutorials.com

import time
from umqttsimple import MQTTClient
import ubinascii
import machine
import micropython
import network
import gc
import ujson
#import config   # my config variables 
from machine import Pin

if station.isconnected() == True:
   from ntptime import settime
   settime()

mqtt_server = '192.168.1.41'
mqtt_port = 1883
client_id = ubinascii.hexlify(machine.unique_id())
sub_topic_power ="POWER"
topic_sub = b'slampher/stat/'+sub_topic_power
topic_pub = b'slampher/cmnd/'+sub_topic_power
keepalive = 0
PRI_pin = 0
PRIMsg = 'OFF'
led_pin = 2
ledMsg = "OFF"
StateOff = 1
StateOn = 0
last_message = 0
message_interval = 5
counter = 0
DevIsEnabled = True

try:
    #if DataJson in globals():      #not working???
    #if DataJson in locals():       #not working???
    mqtt_user =  DataJson["wifi"]["mqtt_user"]
    mqtt_password =  DataJson["wifi"]["mqtt_password"]
    print("DataJson existed!")
except NameError:
    print("DataJson does not exists!")
    DataJson = {
      "APSSID" : "ssid",
      "APpassword" : "ssid_password",
      "STSSID" : "ssid",
      "STpassword" : "ssid_password",
      "mqtt_user" : "User",
      "mqtt_password" : "Pass"  
    }
    import ujson
    with open('config.json') as data_file:
        DataJson = ujson.load(data_file)
    data_file.close
    mqtt_user =  DataJson["wifi"]["mqtt_user"]
    mqtt_password =  DataJson["wifi"]["mqtt_password"]
    print("DataJson Now exists!")

slampher_mqtt = {
   "cmnd" : {"1","POWER"},
   "tele" : {"5","LWT","STATE","INFO1","INFO2","INFO3"},
   "stat" : {"RESULT","POWER"}
}

#slampher/tele/INFO1 = {"Module":"Slampher","Version":"6.6.0(sonoff)","FallbackTopic":"cmnd/DVES_484E85_fb/","GroupTopic":"sonoffs"}
#slampher/tele/INFO2 = {"WebServerMode":"Admin","Hostname":"slampher-3717","IPAddress":"192.168.1.252"}
#slampher/tele/INFO3 = {"RestartReason":"Software/System restart"}
#slampher/tele/STATE = {"Time":"2020-10-10T18:13:59","Uptime":"0T00:00:15","Heap":24,"SleepMode":"Dynamic","Sleep":50,"LoadAvg"19,"POWER":"OFF","Wifi":{"AP":2,"SSId":"MQTTAP","BSSId":"00:23:69:E0:63:4E","Channel":10,"RSSI":76,"LinkCount":1,"Downtime":"0T00:00:05"}}
#slampher/stat/RESULT = {"POWER":"OFF"} 
#slampher/stat/POWER = OFF


mqttJson = {
  "Count" : "0",
  "PRI" : "Off",
  "led" : "Off"
  }


def sub_cb(topic, msg):
  print((topic, msg))
  if topic == topic_sub and msg == b'on':
    led_on()
    print('ESP received On message')
  if topic == topic_sub and msg == b'off':
    led_off()
    print('ESP received off message')
  if topic == topic_sub and msg == b'restart':
    print('ESP received restart message')
    #time.sleep(1)
    machine.reset()

def connect_and_subscribe():
  global client_id, mqtt_server, mqtt_port, mqtt_user, mqtt_password, topic_sub
  client = MQTTClient(client_id, mqtt_server, mqtt_port, mqtt_user, mqtt_password, keepalive)
  client.set_callback(sub_cb)
  client.connect()
  client.subscribe(topic_sub)
  print('Connected to %s MQTT broker'% (mqtt_server))
  print('subscribed to %s topic' % (topic_sub))
  return client

def restart_and_reconnect():
  print('Failed to connect to MQTT broker. Reconnecting...')
  time.sleep(10)
  machine.reset()

def blink_led(val):
  Pin(led_pin, Pin.OUT).value(StateOn)
  time.sleep(val)
  Pin(led_pin, Pin.OUT).value(StateOff)
  print('blinked led!')

def led_on():
  Pin(led_pin, Pin.OUT).value(StateOn)
  mqttJson["led"] = 'On'
  print('led is On!')

def led_off():
  Pin(led_pin, Pin.OUT).value(StateOff)
  mqttJson["led"] = 'Off'  
  print('led is Off!')

def turn_pump_on():
  Pin(relay_pin, Pin.OUT).value(StateOn)
  mqttJson["Relay"] = 'On'
  print('Pump On!')
#  client.publish(topic_pub_state, mqttJson["Relay"])
  
def turn_pump_off():
  Pin(relay_pin, Pin.OUT).value(StateOff)
  mqttJson["Relay"] = 'Off'
  print('Pump Off!') 
#  client.publish(topic_pub_state, mqttJson["Relay"])

try:
  client = connect_and_subscribe()
  blink_led(5)
#  turn_pump_off()
except OSError as e:
  restart_and_reconnect()

while True:
  try:
    client.check_msg()
    if (time.time() - last_message) > message_interval:
      JsonMqtt = ujson.dumps(mqttJson)  
      #client.publish(topic_pub_status, JsonMqtt)
      last_message = time.time()
      counter += 1
      mqttJson["Count"] = counter
      print ('publishing to topic %s' % (topic_pub))
      print ('with message %s' % (mqttJson))
      #print ('last_message is %s' % (last_message))
  except OSError as e:
    restart_and_reconnect()