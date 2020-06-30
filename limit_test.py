import RPi.GPIO as GPIO
import time
import datetime
import sqlite3
import socket
import codecs
from datetime import timedelta
from azure.iot.device import IoTHubDeviceClient, Message

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)


switch6 = 7
switch13 = 11



GPIO.setup(switch6, GPIO.IN)
GPIO.setup(switch13, GPIO.IN)


db = sqlite3.connect('countDB')
c = db.cursor()

#CONNECTION_STRING = "HostName=ProtoHub2.azure-devices.net;DeviceId=CountingPi;SharedAccessKey=i82ITchPwMDSGWVnCqTNO1a7k+10KNAQEDCBb8TvkdY="
CONNECTION_STRING = "HostName=ProtoTestHub1.azure-devices.net;DeviceId=TestPi;SharedAccessKey=yBugeI5Nmgfri43vcYmz/iu/x4q79v2ALkfUxFMGDP8="
MSG_TXT = '{{"6KG": {count_six}, "13KG": {count_thirteen}}}' 


def iothub_client_init():  
    client = IoTHubDeviceClient.create_from_connection_string(CONNECTION_STRING)  
    return client
    
def iothub_client_telemetry_sample_run():
	try:
		client = iothub_client_init()
		mytime =  datetime.datetime.now()
		count_six = 0
		count_thirteen = 0
		stop_shift1 =  mytime.replace(hour = 5, minute = 55, second = 30, microsecond = 0)
		HOST = '10.10.80.26'
		PORT = 8001
		
		
		while True:
			if(GPIO.input(switch6)== True) and (GPIO.input(switch13) == False): #if input detected on bottom switch alone
				count_six = count_six + 1
				time.sleep(0.5)
			if (GPIO.input(switch6) == True) and (GPIO.input(switch13) == True): #if input detected on bottom and top switch
				count_thirteen = count_thirteen + 1
				time.sleep(0.5)
			if(GPIO.input(switch6) == False) and (GPIO.input(switch13) == False):
				count_six = count_six
				count_thirteen = count_thirteen
				time.sleep(0.5)

			Time = datetime.datetime.now()
			d = timedelta(minutes = 30, seconds = 0, microseconds = 0) #time to display readings
			
			if(Time -  mytime >= d):
				print(count_six, count_thirteen)
				print(Time)
				
				mytime = datetime.datetime.now()
				
				#insert values into table COUNTV3
				c.execute("INSERT INTO COUNTV3 (Timestamp, SixKG, ThirteenKG) VALUES(?,?,?)", (Time, count_six, count_thirteen))
				
				#format readings to send to azure
				formatted_t = MSG_TXT.format(count_six = count_six,count_thirteen = count_thirteen)
				message = Message(formatted_t)
				
				#send message to azureIoTHub
				client.send_message(message)	
				
				#s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				#s.connect((HOST, PORT))
				#v = (str(count_six)+','+str(count_thirteen)+','+str(Time))
				#x = bytes(v, encoding='utf8')				
				#s.sendall(x)
				
				
				#check if end of shift and reset counts to zero
				if ((Time) >= (stop_shift1)):
					print("Shift end count: ", count_six, count_thirteen, Time)
					count_six = 0
					count_thirteen = 0
				
				#get new time readings to prevent the if statement from always being true
					mytime = datetime.datetime.now()
					#Time = datetime.datetime.now()
					stop_shift1 =  Time + datetime.timedelta(hours = 6, minutes = 0, seconds = 00, microseconds = 0)
								
				db.commit()
		db.close()
		

	except KeyboardInterrupt:
		GPIO.cleanup()
		
		
if __name__ == '__main__':  
    print ( "Proto Counter" )  
    iothub_client_telemetry_sample_run()	
