##############################################################################
#
# Globals
#
##############################################################################
DEBUG=DEBUG
# WiFi connection information
WIFI_SSID=WIFI_SSID
WIFI_PASS=WIFI_PASS
# MQTT Globals
MQTT_URL = MQTT_URL
MQTT_PORT = MQTT_PORT
MQTT_USER = MQTT_USER
MQTT_PASS = MQTT_PASS
MQTT_TOPIC = MQTT_TOPIC


# useconds to wait for each cycle
CYCLE_WAIT = 300000
# seconds to wait for each debug cycle
DEBUG_WAIT = 30
# ESP8266
PIN_D1=5
PIN_D2=4
PIN_D3=2
PIN_D5=14
PIN_D6=12

##############################################################################
#
# check if the device woke from a deep sleep
#
##############################################################################
def log(msg):
  if(DEBUG):
    print(str(msg))

try:
  from gc import collect
  from machine import deepsleep, reset_cause, DEEPSLEEP_RESET, I2C, Pin
  from time import sleep

  ##############################################################################
  #
  # check if the device woke from a deep sleep
  #
  ##############################################################################
  log('INFO: I\'m alive!')
  cause = reset_cause() 
  if cause  == DEEPSLEEP_RESET:
    log('INFO: reset_cause() == DEEPSLEEP_RESET')
  else:
    log('INFO: Give Deckard a sporting chance. zzz.')
    sleep(5)
  del cause
  del DEEPSLEEP_RESET
  collect()

  ##############################################################################
  #
  # Init led pin (where off is on...)
  #
  ##############################################################################
  if DEBUG:
    log('INFO: Lighting the candle.')
    ledPin = Pin(PIN_D3, Pin.OUT, value=0)

  ##############################################################################
  #
  # Turn on sensors and wait to settle
  #
  ##############################################################################
  log('INFO: Taking the sextant sight.')
  anglesPin = Pin(PIN_D5, Pin.OUT, value=1)
  log('INFO: Tapping the barometer.')
  tempPin = Pin(PIN_D6, Pin.OUT, value=1)
  log('INFO: zzz.')
  sleep(2)

  ##############################################################################
  #
  # get accelerometer angles
  #
  ##############################################################################
  log('INFO: Getting bearings.')
  from gy521 import GY521
  angles=GY521(scl_pin=PIN_D1, sda_pin=PIN_D2).read_angles()
  del GY521
  collect()
  log('INFO: angles={}'.format(angles))
  
  ##############################################################################
  #
  # get environment values
  #
  ##############################################################################
  log('INFO: Checking the weather.')
  from bme280_float import BME280
  values = BME280(i2c=I2C(scl=Pin(5), sda=Pin(4))).values
  del BME280
  collect()
  log('INFO: values={}'.format(values))

  ##############################################################################
  #
  # Turn off sensors
  #
  ##############################################################################
  log('INFO: Putting away sextant.')
  anglesPin.off()
  del anglesPin
  log('INFO: Putting away barometer.')
  tempPin.off()
  del tempPin
  collect()

  ##############################################################################
  #
  # Init Wifi
  #
  ##############################################################################
  log('INFO: Raising the semaphore flags.')
  from network import AP_IF, STA_IF, WLAN
  from ubinascii import hexlify
  # turn off the WiFi Access Point
  ap_if = WLAN(AP_IF)
  ap_if.active(False)
  # connect the device to the WiFi network
  wifi = WLAN(STA_IF)
  active = wifi.active(True)
  connect = wifi.connect(WIFI_SSID, WIFI_PASS)
  # wait until the device is connected to the WiFi network
  MAX_ATTEMPTS = 20
  attempt_count = 0
  while not wifi.isconnected() and attempt_count < MAX_ATTEMPTS:
    attempt_count += 1
    log('INFO: z.')
    sleep(1)
  if attempt_count == MAX_ATTEMPTS:
    log('ERROR: The flag pole is broken.')
  log('INFO: connect={}'.format(connect))
  # Get mac address
  mac = hexlify(wifi.config('mac'),':').decode()
  log('INFO: mac={}'.format(mac))
  # clean up this mess
  del hexlify
  del WLAN
  del AP_IF
  del STA_IF
  del ap_if
  del active
  del connect
  del MAX_ATTEMPTS
  del attempt_count
  del wifi
  collect()
  
  ##############################################################################
  #
  # Init date/time
  #
  ##############################################################################
  log('INFO: Synchronizing time pieces.')
  from ntptime import settime
  gottime = settime()
  log('INFO: gottime={}'.format(gottime))
  del settime
  del gottime
  collect()

  ##############################################################################
  #
  # Setup Message body
  #
  ##############################################################################
  from time import localtime
  ltime=localtime()
  del localtime
  collect()
  utime='{:d}-{:02d}-{:02d}T{:02d}:{:02d}:{:02d}.0'.format(ltime[0],ltime[1],ltime[2],ltime[3],ltime[4],ltime[5])
  log('INFO: utime={}'.format(utime))
  json='{{"id": "{}", "utime": "{}", "x": "{}", "y": "{}", "z": "{}", "temperature": "{}", "pressure": "{}", "humidity": "{}", "DEBUG": "{}"}}'.format(mac, utime, angles[0], angles[1], angles[2], values[0], values[1], values[2], DEBUG)
  log('INFO: json={}'.format(json))
  del ltime
  del utime
  del angles
  del values
  collect()

  ##############################################################################
  #
  # Init MQTT
  #
  ##############################################################################
  log('INFO: Setting up pigeon carrier.')
  from umqtt.robust import MQTTClient
  collect()
  client = MQTTClient(client_id=mac,
    server=MQTT_URL,
    port=MQTT_PORT,
    user=MQTT_USER,
    password=MQTT_PASS,
    ssl=True
    )

  log('INFO:    Releasing a dove.')
  connect = client.connect()
  log('INFO:    connect={}'.format(connect))
  
  publish = client.publish(MQTT_TOPIC, json)
  log('INFO:    publish={}'.format(publish))

  log('INFO: zzz.')
  sleep(1)

  log('INFO:    Retrieving an olive branch.')
  disconnect = client.disconnect()
  log('INFO:    disconnect={}'.format(disconnect))
  
  ##############################################################################
  #
  # Toggle led pin
  #
  ##############################################################################
  if DEBUG:
    log('INFO: Pretty much finished now, blowing out the candle.')
    ledPin.on()

except Exception as e:
  log('ERROR: caught exception {}'.format(e))

finally:
  from time import sleep
  from machine import reset
  try:
    log('INFO: Time to die (or hibernate at least).')
    if (DEBUG):
      log('INFO: DEBUG_WAIT={}, zzz.'.format(DEBUG_WAIT))
      sleep(DEBUG_WAIT)
      reset()
    ##############################################################################
    #
    # Set RTC wakeup
    #
    ##############################################################################
    log('INFO: Setting my wake up call.')
    from machine import deepsleep, RTC, DEEPSLEEP
    rtc = RTC()
    rtc.irq(trigger=rtc.ALARM0, wake=DEEPSLEEP)
    rtc.alarm(rtc.ALARM0, CYCLE_WAIT)
    log('INFO: doing deepsleep')
    deepsleep()
  except Exception as e:
    log('ERROR: caught exception {}'.format(e))
  finally:
    log('ERROR: could not deepsleep, doing busy sleep')
    sleep(CYCLE_WAIT/1000)
    reset()

