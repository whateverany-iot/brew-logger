#!/usr/bin/python
import sys
import os
import paho.mqtt.client as mqtt
import json
import sqlite3
import datetime
import argparse
import logging
import time

#
#
#
#msg='{"id": "de:ad:be:ef:ca:fe", "stime": "2038-01-19 03-14-08", "x": "0.00", "y": "0.00", "z": "0.00", "temperature": "00.00C", "pressure": "1000.00hPa", "humidity": "0.00%", "DEBUG": "True"}'

# The callback for when the client receives a CONNACK response from the server.
def on_connect(_client, _userdata, _flags, _rc):
  logging.info("Connected with result code "+str(_rc))

  # Subscribing in on_connect() means that if we lose the connection and
  # reconnect then subscriptions will be renewed.
  _client.subscribe("/brew/#")

# The callback for when a PUBLISH message is received from the server.
def on_message(_client, _userdata, _msg):
  logging.info('{} {}'.format(_msg.topic,_msg.payload))

  _d = json.loads(_msg.payload)

  _q="""
insert into brews  values (?,?,?,?,?,?,?,?,?)
"""
  _cur.execute(_q,(_d['id'], _d['utime'].replace('T',''), _d['x'], _d['y'], _d['z'], _d['temperature'].replace('C',''), _d['pressure'].replace('hPa',''), _d['humidity'].replace('%',''), bool(_d['DEBUG'])))
  _con.commit()


#
# Setup logging
#
logging.basicConfig(filename='brew_logger.log',level=logging.DEBUG)
logging.debug('BEGIN sub')

try:
  #
  # Get command args
  #
  _parser = argparse.ArgumentParser()
  _parser.add_argument('--mqtt-user', default=os.environ.get('MQTT_USER'))
  _parser.add_argument('--mqtt-pass', default=os.environ.get('MQTT_PASS'))
  _parser.add_argument('--mqtt-host', default=os.environ.get('MQTT_HOST'))
  _parser.add_argument('--mqtt-port', default=os.environ.get('MQTT_PORT'), type=int)
  _parser.add_argument('--db-file', default=os.environ.get('DB_FILE'))
  _parser.add_argument('--db-delete', default=False, action='store_true')
  _args = _parser.parse_args()


  while True:
    try:
      #
      # Open db
      #
      _con = sqlite3.connect(_args.db_file)
      _cur = _con.cursor()

      #
      # 
      #
      try:
        #
        # Delete table
        #
        if _args.db_delete:
          if raw_input("Are you sure? (y/n)") != "y":
            exit()
          _q="""drop table if exists brews"""
          _cur.execute(_q)
        
        #
        # Create table
        #
        _q="""
        CREATE TABLE IF NOT EXISTS brews (
        id TEXT,
        utime DATETIME,
        x FLOAT,
        y FLOAT,
        z FLOAT,
        temperature FLOAT,
        pressure FLOAT,
        humidity FLOAT,
        DEBUG INT,
        PRIMARY KEY(id,utime)
        ) 
        """
        _cur.execute(_q)
        
        #
        # Open client
        #
        logging.info('mqtt.Client')
        _client = mqtt.Client()
        logging.info('_client.on_connect = on_connect')
        _client.on_connect = on_connect
        logging.info('_client.on_message = on_message')
        _client.on_message = on_message
        
        logging.info('_client.tls_set()')
        _client.tls_set()
        #
        logging.info('_client.tls_insecure_set(True)')
        _client.tls_insecure_set(True)
        #
        logging.info('_client.username_pw_set({}, "XXXXXXXX") '.format(_args.mqtt_user))
        _client.username_pw_set(_args.mqtt_user, _args.mqtt_pass) 
        #
        logging.info('_client.connect("{}", {}, 30)'.format(_args.mqtt_host, _args.mqtt_port))
        _client.connect(_args.mqtt_host, _args.mqtt_port, 30)
        
        # Wait for messages
        _client.loop_forever()
    
      except Exception as e:
        logging.error('caught exception {}'.format(e))
  
      finally: 
        _cur.close()
        _con.close()
    except Exception as e:
      logging.error('caught exception {}'.format(e))
  
    finally: 
      logging.error('Processing loop crashed, taking a rest')
      time.sleep(60)

except Exception as e:
  logging.error('caught exception {}'.format(e))

finally:
  logging.debug('END sub')

