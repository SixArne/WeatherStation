import os
import numpy as np
import time
from sense_hat import SenseHat

sense = SenseHat()


def get_cpu_temp():
  res = os.popen("vcgencmd measure_temp").readline()
  t = float(res.replace("temp=","").replace("'C\n",""))
  return(t)

def get_smooth(x):
  if not hasattr(get_smooth, "t"):
    get_smooth.t = [x,x,x]
  get_smooth.t[2] = get_smooth.t[1]
  get_smooth.t[1] = get_smooth.t[0]
  get_smooth.t[0] = x
  xs = (get_smooth.t[0]+get_smooth.t[1]+get_smooth.t[2])/3
  return(xs)

# Because the temperature sensor is close to the CPU
# the temperature is incorrect, so here we apply some temperature
# fixes. Credit goes to YetAnotherArduinoBlog
def get_temperature_measurement():
    tfh = sense.get_temperature_from_humidity()
    tfp = sense.get_temperature_from_pressure()
    tfc = get_cpu_temp()

    t = (tfh+tfp)/2
    t_corr = t - ((tfc-t)/1.5)
    return get_smooth(t_corr)


def flash_light(color, clear_time):
   a = np.empty((64, 3), dtype=int) 
   a[:] = color
   sense.set_pixels(a)

   time.sleep(clear_time)
   sense.clear()

def get_sense():
   return sense