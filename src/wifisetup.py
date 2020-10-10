def do_connect():
    import network
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('connecting to network...')
        #wlan.connect('MQTTAP', 'Mqtt_pass$')
        wlan.connect('XboxWifi', '$!F0rbin1$')
        while not wlan.isconnected():
            #pass
            time.sleep_ms(500)
            print('Connecting')
    print('network config:', wlan.ifconfig())
    
    