# Complete project details at https://RandomNerdTutorials.com

import utime
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
keepalive = 0
led_pin = 2
ledMsg = "OFF"
StateOff = 1
StateOn = 0
last_message = 0
message_interval = 5
counter = 0
IsBilgePumpDev = False
IsslampherDev = True
DevIsEnabled = True

if IsBilgePumpDev  :
    #for sonoff SV Ver 1.0 relay on pin 12
    #for sonoff SV Ver 1.0 botton on pin 0
    # button_pin = 0
    #for sonoff SV Ver 1.0 led on pin 13
    #for TB-IOTMCU relay relay on pin 0
    #for TB-IOTMCU relay led on pin 2
    relay_pin = 0
    relayMsg = 'Off'
    sub_topic_cmnd ="/cmnd"
    sub_topic_status ="/status"
    sub_topic_state ="/state"
    topic_sub = b'bilgpump'
    topic_pub_status = b'bilgpump'
    topic_pub_state = b'bilgpump'
    mqttJson = {
      "Count" : "0",
      "Relay" : "Off",
      "led" : "Off"
    }
elif IsslampherDev:
    PRI_pin = 3
    PRIMsg = 'OFF'
    PRIStateOn = "On"
    PRIStateOff = "Off"
    sub_topic_power ="/cmnd/POWER"
    sub_topic_stat_result = "/stat/RESULT"
    sub_topic__stat_power ="/stat/POWER"
    sub_topic_tele_state = "/tele/STATE"
    sub_topic_stat_PRI = "/stat/PRI"
    topic_sub = b'slampher'
    topic_pub = b'slampher'
    mqttJson = {
      "Count" : "0",
      "PRI" : "Off",
      "led" : "Off"
      }
    slampher_mqtt = {
       "cmnd" : {"POWER"},
       "tele" : {"LWT","STATE","INFO1","INFO2","INFO3"},
       "stat" : {"RESULT","POWER"}
    }
# Notes
#slampher/tele/INFO1 = {"Module":"Slampher","Version":"6.6.0(sonoff)","FallbackTopic":"cmnd/DVES_484E85_fb/","GroupTopic":"sonoffs"}
#slampher/tele/INFO2 = {"WebServerMode":"Admin","Hostname":"slampher-3717","IPAddress":"192.168.1.252"}
#slampher/tele/INFO3 = {"RestartReason":"Software/System restart"}
#slampher/tele/STATE = {"Time":"2020-10-10T18:13:59","Uptime":"0T00:00:15","Heap":24,"SleepMode":"Dynamic","Sleep":50,"LoadAvg"19,"POWER":"OFF","Wifi":{"AP":2,"SSId":"MQTTAP","BSSId":"00:23:69:E0:63:4E","Channel":10,"RSSI":76,"LinkCount":1,"Downtime":"0T00:00:05"}}
#slampher/stat/RESULT = {"POWER":"OFF"} 
#slampher/stat/POWER = OFF

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


def sub_cb(topic, msg):
    print((topic, msg))
    if IsBilgePumpDev  :
        if topic == topic_sub and msg == b'on':
            led_on()
            turn_pump_on()
            print('ESP received On message')
        if topic == topic_sub and msg == b'off':
            turn_pump_off()
            led_off()
            print('ESP received off message')   
    if topic == topic_sub and msg == b'restart':
       print('ESP received restart message')
       machine.reset()

def connect_and_subscribe(subtopic):
  global client_id, mqtt_server, mqtt_port, mqtt_user, mqtt_password, topic_sub
  client = MQTTClient(client_id, mqtt_server, mqtt_port, mqtt_user, mqtt_password, keepalive)
  client.set_callback(sub_cb)
  client.connect()
  subscribeTotopic = topic_sub+subtopic
  client.subscribe(subscribeTotopic)
  print('Connected to %s MQTT broker'% (mqtt_server))
  print('subscribed to %s topic' % (subscribeTotopic))
  return client

def restart_and_reconnect():
  print('Failed to connect to MQTT broker. Reconnecting...')
  utime.sleep(10)
  machine.reset()

def blink_led(val):
  Pin(led_pin, Pin.OUT).value(StateOn)
  utime.sleep(val)
  Pin(led_pin, Pin.OUT).value(StateOff)
  utime.sleep(val/2)
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
  
def turn_pump_off():
  Pin(relay_pin, Pin.OUT).value(StateOff)
  mqttJson["Relay"] = 'Off'
  print('Pump Off!')

try:
  
  blink_led(5)
  if IsBilgePumpDev :
     turn_pump_off()
     client = connect_and_subscribe(sub_topic_cmnd)
  elif IsslampherDev:
     client = connect_and_subscribe(sub_topic_stat_PRI)       
except OSError as e:
  restart_and_reconnect()

while True:
  try:
    client.check_msg()
    blink_led(5)
    if (utime.time() - last_message) > message_interval:
      JsonMqtt = ujson.dumps(mqttJson)
      if IsBilgePumpDev :
        pubtopic = topic_pub+sub_topic_status
        client.publish(pubtopic, JsonMqtt)
      elif IsslampherDev:
        PRIState = Pin(PRI_pin, Pin.IN).value()
        if PRIState == True and mqttJson["PRI"] == 'Off':          # motion
          pubtopic = topic_pub+sub_topic_power
          client.publish(pubtopic, PRIStateOn)
          mqttJson["PRI"] = 'On'
        elif  PRIState == False and mqttJson["PRI"] == 'On':
          pubtopic = topic_pub+sub_topic_power
          client.publish(pubtopic, PRIStateOff)            
          mqttJson["PRI"] = 'Off'  
        pubtopic = topic_pub+sub_topic_stat_PRI
        client.publish(pubtopic, JsonMqtt)          
      last_message = utime.time()
      counter += 1
      mqttJson["Count"] = counter
      print ('publishing to topic %s' % (topic_pub))
      print ('with message %s' % (mqttJson))
      #print ('last_message is %s' % (last_message))
  except OSError as e:
    restart_and_reconnect()