from pirc522 import RFID
import OSC
import RPi.GPIO as GPIO  
import time
import socket
import json

GPIO.setwarnings(False)


c = OSC.OSCClient()
c.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
c.connect(('192.168.0.255', 7000))

rdr = RFID(pin_ce=24, pin_irq=12, pin_rst=7)
# rdr2 = RFID(pin_ce=24, pin_irq=12)

# working ce pins 24,26,32,36,38,40

lastuid=False

data = json.load(open('mapping.json'))
mapping = data['mapping']
layer = data['layer']

def send(addr, val):
  oscmsg = OSC.OSCMessage()
  oscmsg.setAddress(addr)
  oscmsg.append(val)
  c.send(oscmsg)

def trigger(uid):
  if uid in mapping:
    print mapping[uid]
    send(layer+mapping[uid], 1)

def untrigger():
  send(layer+"clip1/connect", 1)

try:  
  on = False
  nocount = 0
  while True:
    #rdr.wait_for_tag()

    rdr.init()
    rdr.irq.clear()
    rdr.dev_write(0x04, 0x00)
    rdr.dev_write(0x02, 0xA0)

    # wait for it
    waiting = True
    rdr.dev_write(0x09, 0x26)
    rdr.dev_write(0x01, 0x0C)
    rdr.dev_write(0x0D, 0x87)
    waiting = not rdr.irq.wait(0.1)

    rdr.irq.clear()
    rdr.init()

    if not waiting:
      (e, tag_type) = rdr.request()
      (e, uid) = rdr.anticoll()
      uid = reduce(lambda x, char: x+format(char, 'x'), uid, "")
      nocount = 0
      if not on:
        on = uid
        print uid
        trigger(uid)
    else:
      if on:
        if nocount > 0:
          untrigger()
          on = False
          print 'nope'
        else:
          print nocount
          nocount = nocount + 1  
      
  
except KeyboardInterrupt:  
  print "\n"
  
except:  
    print "Other error or exception occurred!"  
finally:  
    rdr.reset()
    rdr.cleanup()
