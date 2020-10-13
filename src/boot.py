# This file is executed on every boot (including wake-boot from deepsleep)

import uos, machine
import gc
import esp
import time
from umqttsimple import MQTTClient
import ubinascii
import micropython
import network
import webrepl

#uos.dupterm(None, 1) # disable REPL on UART(0)
esp.osdebug(None)
gc.collect()

org_freq = machine.freq()          # get the current frequency of the CPU
print('Machine freq was %s' % (org_freq))
# do not over clock, no need for now
# machine.freq(160000000)            # set the CPU frequency to 160 MHz
# print('Machine freq set to %s' % (160000000))

DevIsEnabled = True
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
ssid =  DataJson["wifi"]["STSSID"]
ssid_password =  DataJson["wifi"]["STpassword"]

AP = network.WLAN(network.AP_IF)
AP.active(False)

station = network.WLAN(network.STA_IF)
station.active(True)
station.connect(ssid, ssid_password)

while station.isconnected() == False:
    #pass
    time.sleep_ms(500)
    print('Connecting')
print('Connection successful')
print(station.ifconfig())

if station.isconnected() == True:
   import webrepl
   webrepl.start()    # start webrepl

if station.isconnected() == True:
   time.sleep(5)
   from ntptime import settime
   settime()
