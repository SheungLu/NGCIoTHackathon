'''
Main code that gathers sensor data and publishes the data as a message 
on MQTT client provided by Amazon Web Services IoT platform.
'''
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import sys
import logging
import time
import getopt
import PCF8591 as ADC
import RPi.GPIO as GPIO
import LCD1602
import time
import math

colors = [0xFF0000, 0x00FF00, 0x0000FF, 0xFFFF00, 0xFF00FF, 0x00FFFF]
R = 16
G = 15
B = 13
TRIG = 11
ECHO = 12
Rt = 1

# Custom MQTT message callback
def customCallback(client, userdata, message):
	print("Received a new message: ")
	print(message.payload)
	print("from topic: ")
	print(message.topic)
	print("--------------\n\n")

	
#Setup MQTT client to communicate with AWS IoT platform
def setupMQTT():
	# Usage
	usageInfo = """Usage:

	Use certificate based mutual authentication:
	python basicPubSub.py -e <endpoint> -r <rootCAFilePath> -c <certFilePath> -k <privateKeyFilePath>

	Use MQTT over WebSocket:
	python basicPubSub.py -e <endpoint> -r <rootCAFilePath> -w

	Type "python basicPubSub.py -h" for available options.
	"""
	# Help info
	helpInfo = """-e, --endpoint
		Your AWS IoT custom endpoint
	-r, --rootCA
		Root CA file path
	-c, --cert
		Certificate file path
	-k, --key
		Private key file path
	-w, --websocket
		Use MQTT over WebSocket
	-h, --help
		Help information


	"""

	# Read in command-line parameters
	useWebsocket = False
	host = "a19zzgl8s6zfsq.iot.us-east-1.amazonaws.com"
	rootCAPath = "rootCA.crt"
	certificatePath = "88df1a0b0b-certificate.pem.crt"
	privateKeyPath = "88df1a0b0b-private.pem.key"
	try:
		opts, args = getopt.getopt(sys.argv[1:], "hwe:k:c:r:", ["help", "endpoint=", "key=","cert=","rootCA=", "websocket"])
		#if len(opts) == 0:
			#raise getopt.GetoptError("No input parameters!")
		for opt, arg in opts:
			if opt in ("-h", "--help"):
				print(helpInfo)
				exit(0)
			if opt in ("-e", "--endpoint"):
				host = arg
			if opt in ("-r", "--rootCA"):
				rootCAPath = arg
			if opt in ("-c", "--cert"):
				certificatePath = arg
			if opt in ("-k", "--key"):
				privateKeyPath = arg
			if opt in ("-w", "--websocket"):
				useWebsocket = True
	except getopt.GetoptError:
		print(usageInfo)
		exit(1)

	# Missing configuration notification
	missingConfiguration = False
	if not host:
		print("Missing '-e' or '--endpoint'")
		missingConfiguration = True
	if not rootCAPath:
		print("Missing '-r' or '--rootCA'")
		missingConfiguration = True
	if not useWebsocket:
		if not certificatePath:
			print("Missing '-c' or '--cert'")
			missingConfiguration = True
		if not privateKeyPath:
			print("Missing '-k' or '--key'")
			missingConfiguration = True
	if missingConfiguration:
		exit(2)

	# Configure logging
	logger = logging.getLogger("AWSIoTPythonSDK.core")
	logger.setLevel(logging.DEBUG)
	streamHandler = logging.StreamHandler()
	formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
	streamHandler.setFormatter(formatter)
	logger.addHandler(streamHandler)

	# Init AWSIoTMQTTClient
	global myAWSIoTMQTTClient
	if useWebsocket:
		myAWSIoTMQTTClient = AWSIoTMQTTClient("basicPubSub", useWebsocket=True)
		myAWSIoTMQTTClient.configureEndpoint(host, 443)
		myAWSIoTMQTTClient.configureCredentials(rootCAPath)
	else:
		myAWSIoTMQTTClient = AWSIoTMQTTClient("basicPubSub")
		myAWSIoTMQTTClient.configureEndpoint(host, 8883)
		myAWSIoTMQTTClient.configureCredentials(rootCAPath, privateKeyPath, certificatePath)

	# AWSIoTMQTTClient connection configuration
	myAWSIoTMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
	myAWSIoTMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
	myAWSIoTMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
	myAWSIoTMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
	myAWSIoTMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec

	# Connect and subscribe to AWS IoT
	myAWSIoTMQTTClient.connect()
	myAWSIoTMQTTClient.subscribe("sensor_data/temperature/", 1, customCallback)
	myAWSIoTMQTTClient.subscribe("sensor_data/sonar/", 1, customCallback)
	myAWSIoTMQTTClient.subscribe("sensor_data/gas/", 1, customCallback)
	myAWSIoTMQTTClient.subscribe("sensor_data/flame/", 1, customCallback)
	

#setup sensors
def setup(Rpin, Gpin, Bpin):
	global pins
	global p_R, p_G, p_B
	ADC.setup(0x48)
	pins = {'pin_R': Rpin, 'pin_G': Gpin, 'pin_B': Bpin}
	GPIO.setmode(GPIO.BOARD)       # Numbers GPIOs by physical location
	GPIO.setup(TRIG, GPIO.OUT)
	GPIO.setup(ECHO, GPIO.IN)
	
	for i in pins:
		GPIO.setup(pins[i], GPIO.OUT)   # Set pins' mode is output
		GPIO.output(pins[i], GPIO.HIGH) # Set pins to high(+3.3V) to off led
	
	p_R = GPIO.PWM(pins['pin_R'], 2000)  # set Frequece to 2KHz
	p_G = GPIO.PWM(pins['pin_G'], 1999)
	p_B = GPIO.PWM(pins['pin_B'], 5000)
	
	p_R.start(100)      # Initial duty Cycle = 0(leds off)
	p_G.start(100)
	p_B.start(100)
	
	#setup LCD
	LCD1602.init(0x27, 1)	# init(slave address, background light)
	LCD1602.write(0, 0, 'Ultrasonic Range:')
	LCD1602.write(1, 1, '...')
	print 'Done sensor setup'
	time.sleep(2)
	setupMQTT()
	print 'Done AWS_IOT_MQTT setup'
	time.sleep(2)

def distance():
	GPIO.output(TRIG, 0)
	time.sleep(0.000002)

	GPIO.output(TRIG, 1)
	time.sleep(0.00001)
	GPIO.output(TRIG, 0)

	
	while GPIO.input(ECHO) == 0:
		a = 0
	time1 = time.time()
	while GPIO.input(ECHO) == 1:
		a = 1
	time2 = time.time()

	during = time2 - time1
	return during * 340 / 2 * 100


def map(x, in_min, in_max, out_min, out_max):
	return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def off():
	for i in pins:
		GPIO.output(pins[i], GPIO.HIGH)    # Turn off all leds

def setColor(col):   # For example : col = 0x112233
	R_val = (col & 0xff0000) >> 16
	G_val = (col & 0x00ff00) >> 8
	B_val = (col & 0x0000ff) >> 0

	R_val = map(R_val, 0, 255, 0, 100)
	G_val = map(G_val, 0, 255, 0, 100)
	B_val = map(B_val, 0, 255, 0, 100)
	
	p_R.ChangeDutyCycle(100-R_val)     # Change duty cycle
	p_G.ChangeDutyCycle(100-G_val)
	p_B.ChangeDutyCycle(100-B_val)

def loop():
	global Rt
	loops =0
	while True:
		#get sensor data
		dis = distance()
		if (dis > 120):
			dis = 120
			
		d_gas = ADC.read(2)
		d_flame = ADC.read(1)
		d_temp = ADC.read(3)
		Vr = 5 * float(d_temp) / 255
		try:
			Rt = 10000 * Vr / (5 - Vr)
		except ZeroDivisionError:
			print('temp is 255')
			
		temp = 1/(((math.log(Rt / 10000)) / 3950) + (1 / (273.15+25)))
		temp = temp - 273.15
		
		#print locally
		dstring = '{0:.2f}'.format(dis) + ' cm, Gas:' + '{}'.format(d_gas)
		print dstring
		#LCD1602.write(1, 1, dstring)
		LCD1602.write(1, 1, 'Flame:' + '{}'.format(d_flame))
		if (dis > 50):
			setColor(0x00FF00)
		elif (dis > 25):
			setColor(0x00FFFF)
		else:
			setColor(0xFF0000)
		
		#publish
		if (loops % 7==0):
			myAWSIoTMQTTClient.publish("sensor_data/temperature/", str(temp), 1)
			myAWSIoTMQTTClient.publish("sensor_data/sonar/", str(dis), 1)
			myAWSIoTMQTTClient.publish("sensor_data/gas/", str(d_gas), 1)
			myAWSIoTMQTTClient.publish("sensor_data/flame/", str(255-d_flame), 1)
			
		if(loops>100):
			loops = 0
		
		
		loops = loops+1
		print("loop: "+str(loops))
		time.sleep(0.1)

def destroy():
	p_R.stop()
	p_G.stop()
	p_B.stop()
	off()
	GPIO.cleanup()
	print("exiting...")
	
if __name__ == "__main__":
	try:
		setup(R, G, B)
		loop()
	except KeyboardInterrupt:
		destroy()
