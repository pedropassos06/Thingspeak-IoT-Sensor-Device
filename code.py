import time
import board
import busio
import analogio
import adafruit_am2320

#photocell is connected to pin A5 on the microcontroller
photocell = analogio.AnalogIn(board.A5)

#conversion from analog value to respective voltage
def analog_voltage(adc):
  return adc.value / 65535 * adc.reference_voltage

# create the I2C shared bus
i2c = busio.I2C(board.SCL, board.SDA)
am = adafruit_am2320.AM2320(i2c)

light = photocell.value
voltage = analog_voltage(photocell)

#bidirectional serial protocol that uses a mutual baud rate instead of a shared clock line.
uart = busio.UART(board.TX, board.RX, baudrate=115200, bits=8, parity=None, stop=1)

#API requests that will write data to channel. field 1 will be added to this request later on.
update = "GET https://api.thingspeak.com/update?api_key=PUT_YOUR_THINGSPEAK_KEY_HERE"

#defining fields. variables will be added to API write feed request at the end. more fields can be added if needed
field1 = '&field1='
field2 = '&field2='
field3 = '&field3='

#Set wifi mode
uart.write(bytes("AT+CWMODE=1\r\n",'utf-8'))   #mode 1 means station mode (client), 2 means softAP, 3m means dual mode
print("Set to station mode (client)")
time.sleep(2)

#ESP8622 connects to router
uart.write(bytes('AT+CWJAP="PUT_YOUR_WIFI_NAME_HERE","PASSWORD_HERE"\r\n', 'utf-8'))   #wifi name and password
print("Connected to WIFI: WIFI_NAME")
time.sleep(2)
print("Synchronizing...")
data = uart.readline()
time.sleep(2)

while True:
   #reads sensors and reports to serial monitor
   light = photocell.value
   voltage = analog_voltage(photocell)
   print('Photoresistor value: {0} voltage: {1}V'.format(light, voltage))
   print("Temperature: ", am.temperature)
   print("Humidity: ", am.relative_humidity)
   
   #defining fields. variables will be added to API write feed request at the end. more fields can be added if needed
   field1 = '&field1='
   field2 = '&field2='
   field3 = '&field3='

   #defines what is going to be sent to field. data1 follows '&field1='. more data can be added if needed
   data1 = str(voltage)
   data2 = str(am.temperature)
   data3 = str(am.relative_humidity)

   #defines API request
   writeFeed = update + field1 + data1 + field2 + data2 + field3 + data3 + ' HTTP/1.1\r\nHost: api.thingspeak.com\r\n\r\n'

   #ESP8622 connects to the server as TCP client
   uart.write(bytes('AT+CIPSTART="TCP","api.thingspeak.com",80\r\n','utf-8'))  #protocol, website, and port
   time.sleep(2)

   #ESP8622 sends data to the server
   uart.write(bytes("AT+CIPSEND="+str(len(writeFeed))+"\r\n", 'utf-8'))  #set data length which will be sent, such as 86 bytes
   time.sleep(2)

   #writes channel feed
   uart.write(bytes(writeFeed,'utf-8'))
   print(writeFeed)
   time.sleep(10)

   print("Next data point")
