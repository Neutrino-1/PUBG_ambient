import numpy as np 
from PIL import ImageGrab
import cv2
import math
import serial
import time

file = open("damage.txt",'a+')
previous_health = 0
previous_damage = 0
com = serial.Serial('com4',9600)

def calculate(edges):

	''' Calculating the damage by measuring the difference is length 
		of the total health bar and health bar after damage
		(remaing_health)'''

	# variable to keep track of previous remaing health
	global previous_health
	sum_of_white_pixel = 0
	
	#Total health bar width in numpy array (a)
	Total_health = len(edges)
	#Total health bar height in numpy array (b)
	Total_vertical_pixel = len(edges)
	
	#loop through all the (a) rows
	'''
	   b
	   ^
	   |
	   0000000000000000002550000000  <- a
	   0000000000000000002550000000  <- a
	   0000000000000000002550000000  <- a
	   0000000000000000002550000000  <- a
	   0000000000000000002550000000  <- a'''

	correctEdge = False
	for edge in edges:
		#detecting the white pixels(255) by eliminating the nonzero indices
		white_pixel = np.nonzero(edge)[0]
		
		no_pixel_in_one_row = len(white_pixel)

		if no_pixel_in_one_row < 1:
			break
		else:
			if (white_pixel[0] - white_pixel[-1]) <= 4:
				correctEdge = True
			else:
				break
		# if the multiple lines arises taking the average of each (a) row
		avg_of_white_pixel = sum(white_pixel)/len(white_pixel)
		
		# if the image obtained has no edge set the average to 0
		if math.isnan(avg_of_white_pixel):
			avg_of_white_pixel = 0

		#taking sum of all white pixel in the (a) rows
		sum_of_white_pixel += int(avg_of_white_pixel)
	
	if(correctEdge):
		#remaing health is calculate by taking the average of white pixels vertical (b colums)
		remaing_health = int(sum_of_white_pixel/Total_vertical_pixel)

		#if remain_health is 0 during staring of the program set it equal to total health
		if(remaing_health == 0):
			remaing_health = Total_health

		#Damage is calculated by total health - remaing health 
		damage = Total_health - remaing_health
		
		#for glitch fixes
		glitch = abs(previous_health-remaing_health)

		#error value to fix the glitch
		error = 6
		#file.write(str(damage)+"\n")
		#Damage value changes only if the glitch is less than error
		if damage != 0 and glitch >= error:
			global previous_damage	
			healing = True

			hitRate = damage - previous_damage

			print("pre damage:",previous_damage)
			print("hitRate: ",hitRate)

			if damage > previous_damage:
				healing = False
			else:
				healing = True
			
			print("healing:",healing)

			if not healing   and hitRate < 10:
				hitRate = 1

			elif not healing and hitRate < 50:
				hitRate = 2

			elif not healing and hitRate < 100:
				hitRate = 3

			elif not healing and hitRate > 100:
				hitRate = 4

			elif healing     and hitRate > -10:
				hitRate = 5

			elif healing 	 and hitRate > -50:
				hitRate = 6

			elif healing     and hitRate > -100:
				hitRate = 7

			elif healing     and hitRate < -100:
				hitRate = 8

			arduino_control(hitRate)
			print("hitRate: ",hitRate)
			previous_damage = damage
			previous_health = remaing_health
			print("Damage=",damage)



def  Image_processing():
	'''Getting the Image from the screen and find the edge of the health bar'''

	#Grabbing the image from screen using pillow library
	#converting the image to numpy array to use the image with cv2 library
	screen = np.array(ImageGrab.grab(bbox = (550,745,815,758)))
	
	cvt_image = cv2.cvtColor(screen,cv2.COLOR_BGR2RGB)
	#using open cv2 to gray out the image grab
	gray_image = cv2.cvtColor(cvt_image, cv2.COLOR_BGR2GRAY)

	#blur the gray image to remove noise and to averaging the color
	blurred = cv2.bilateralFilter(gray_image,15,65,65)

	#converting the blurred image to pure black(0) and white(255) binary image
	thresh = cv2.threshold(blurred, 150,200, cv2.THRESH_BINARY)[1]
	
	#finding the edge of the thresh image
	edges = cv2.Canny(thresh,100,150)

	#displaying the edge and thresh image
	cv2.imshow('Original',cvt_image)
	cv2.imshow('Edge_Detection',edges)
	cv2.imshow('After_processing',thresh)

	#function to calculate the damage
	calculate(edges)


	#function to send data to arduino
	'''
	0 -> pin 10 low
	1 -> pin 10 high
	2 -> pin 10 fade high and low
	3 -> pin l1 high
	4 -> pin 11 low
	5 -> pin 11 fade high and low
	'''

def arduino_control(hitRate):
	if hitRate == 1 :
		com.write(b'1')
		time.sleep(0.6)
		com.write(b'0')
	elif hitRate == 2:
		com.write(b'1')
		time.sleep(1)
		com.write(b'0')
	elif hitRate == 3:
		com.write(b'2')
		time.sleep(2)
		com.write(b'0')
	elif hitRate == 4:
		com.write(b'2')
		time.sleep(3)
		com.write(b'0')
	elif hitRate == 5:
		com.write(b'3')
		time.sleep(0.6)
		com.write(b'4')
	elif hitRate == 6:
		com.write(b'3')
		time.sleep(1)
		com.write(b'4')
	elif hitRate == 7:
		com.write(b'5')
		time.sleep(1)
		com.write(b'4')
	elif hitRate == 8:
		com.write(b'5')
		time.sleep(1)
		com.write(b'4')

#infinite looop
while (True):
	#function to grab the image from screen and process it to find egde
	Image_processing()
	#press 'q' to quit the program (Make sure caps is off)
	if cv2.waitKey(25) & 0xFF == ord('q'):
		cv2.destroyAllWindows()
		break
	