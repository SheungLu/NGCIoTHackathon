import time
import RPi.GPIO as GPIO


# Moving the car

FWD_PIN = 6
BKD_PIN = 13
LFT_PIN = 19
RGT_PIN = 26
OBS_PIN = 5
STRAIGHT_TIME = 2 #CHANGE TO CHANGE MOVEMENT DISTANCE
TURN_TIME = 1


def setup():
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(LFT_PIN, GPIO.OUT) #Left
	GPIO.setup(RGT_PIN, GPIO.OUT) #Right
	GPIO.setup(FWD_PIN, GPIO.OUT) #Forward
	GPIO.setup(BKD_PIN, GPIO.OUT) #Backward
	GPIO.setup(OBS_PIN, GPIO.IN) #Collision avoidance
	
	global pFWD, pBKD, pLFT, pRGT
	pFWD = GPIO.PWM(FWD_PIN, 100)  # set Frequece to 2KHz
	pBKD = GPIO.PWM(BKD_PIN, 100)
	pLFT = GPIO.PWM(LFT_PIN, 100)
	pRGT = GPIO.PWM(RGT_PIN, 100)
	


def setLeft() : 
    GPIO.output(LFT_PIN, True)
    GPIO.output(RGT_PIN, False)
    

def setRight() :
    GPIO.output(LFT_PIN, False)
    GPIO.output(RGT_PIN, True)
    

def setStraight() :
    GPIO.output(LFT_PIN, False)
    GPIO.output(RGT_PIN, False)
    

def simpleForward(movementTime):
	setStraight()
	GPIO.output(FWD_PIN, True)
	GPIO.output(BKD_PIN, False)
	time.sleep(movementTime)
	GPIO.output(FWD_PIN, True)
	GPIO.output(BKD_PIN, True)

def pwmFWD(movementTime):
	setStraight()
	pFWD.start(50)
	
	time.sleep(movementTime)
	pFWD.stop()
	
	GPIO.output(FWD_PIN, True)
	GPIO.output(BKD_PIN, True)

	
def turnRight(movementTime):
	setRight()
	GPIO.output(FWD_PIN, True)
	GPIO.output(BKD_PIN, False)
	time.sleep(movementTime)
	GPIO.output(FWD_PIN, True)
	GPIO.output(BKD_PIN, True)

def pwmRGT(movementTime):
	setRight()
	pFWD.start(75)
	pBKD.stop()
	time.sleep(movementTime)
	pFWD.stop()
	pBKD.stop()
	GPIO.output(FWD_PIN, True)
	GPIO.output(BKD_PIN, True)

def moveForward(movementTime) :
	print("moving forward")
	print time.asctime(time.localtime(time.time()))
	GPIO.output(FWD_PIN, True)
	GPIO.output(BKD_PIN, False)
	
	start = time.time()  
	timeout = start + movementTime
	print time.asctime( time.localtime(timeout) )

	while True :
		if time.time() > timeout :
			break
		if (GPIO.input(OBS_PIN)) :
			print("Obstacle Detected!")
			break
	print("stopping")
	print time.asctime( time.localtime(time.time()) )
	GPIO.output(FWD_PIN, False)
	GPIO.output(BKD_PIN, False)
	time.sleep(1)

def moveBackward(movementTime) :
    GPIO.output(FWD_PIN, False)
    GPIO.output(BKD_PIN, True)
    time.sleep(movementTime)
    GPIO.output(FWD_PIN, False)
    GPIO.output(BKD_PIN, False)
    
def stop() :
    setStraight()
    GPIO.output(FWD_PIN, False)
    GPIO.output(BKD_PIN, False)
     
def driveLoop():
	GPIO.output(BKD_PIN, False)
	pFWD.start(50)
	pRGT.start(0)
	
	while True:
		if (GPIO.input(OBS_PIN)) :
			pFWD.ChangeDutyCycle(0)
			continue 
		time.sleep(STRAIGHT_TIME)
		pRGT.ChangeDutyCycle(50)
		pFWD.ChangeDutyCycle(50)
			
		time.sleep(STRAIGHT_TIME)
		pRGT.ChangeDutyCycle(0)
		pFWD.ChangeDutyCycle(50)
			
		

def destroy():
	pFWD.stop()
	#pBKD.stop()
	pLFT.stop()
	pRGT.stop()
	GPIO.cleanup()
	print("exiting...")

if __name__ == "__main__":
	try:
		setup()
		time.sleep(1)
		driveLoop()
	except KeyboardInterrupt:
		destroy()

