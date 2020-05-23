```
  _                              _                             
 | |                            | |                            
 | |__  _ __ _____      ________| | ___   __ _  __ _  ___ _ __ 
 | '_ \| '__/ _ \ \ /\ / /______| |/ _ \ / _` |/ _` |/ _ \ '__|
 | |_) | | |  __/\ V  V /       | | (_) | (_| | (_| |  __/ |   
 |_.__/|_|  \___| \_/\_/        |_|\___/ \__, |\__, |\___|_|   
                                          __/ | __/ |          
                                         |___/ |___/            
```

Brew logger based on ideas from https://github.com/universam1/iSpindel/blob/master/docs/README_en.md

This project uses micropython on ESP8266 and a self hosted python data logger.

Load https://docs.micropython.org/en/latest/esp8266/tutorial/intro.html


Create compiled libraries
Get http://micropython.org/download/
Create the compiled libraries `micropython/mpy-cross/mpy-cross input.py`

```
bme280_float.mpy
gy521.mpy
imu.mpy
logging.mpy
robust.mpy
umqttsimple.mpy
vector3d.mpy
```

craft and copy `boot.py` and `main.py` to esp8266
