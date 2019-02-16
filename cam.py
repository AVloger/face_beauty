# -*- coding:utf-8 -*-
#!/usr/bin/env python

import cv2
import datetime
import sys
import shutil
from face import FaceAPI
from face import DBConnect
import RPi.GPIO as GPIO
import time
import signal
import atexit

atexit.register(GPIO.cleanup)

pin = 7                         ## 使用7号引脚
pin_led = 12
GPIO.setmode(GPIO.BOARD)        ## 使用BOARD引脚编号，此外还有 GPIO.BCM
GPIO.setup(pin, GPIO.OUT)       ## 设置7号引脚输出
GPIO.setup(pin_led, GPIO.OUT)
p = GPIO.PWM(pin,50)
p.start(0)

def door_open():
	for i in range(0,360,10):
		p.ChangeDutyCycle(12.5-5*i/360)
def door_close():
	for i in range(0,360,10):
		p.ChangeDutyCycle(7.5-5*i/360)	 
reload(sys)
sys.setdefaultencoding('utf8')
conn = DBConnect.dbconnect()
cur = conn.cursor()
def get_detail():
	cur.execute("select * from face_data where face_token='%s'"%face_token)
	line=cur.fetchone()
	stuID,stuname,gender=line[0],line[1],line[3]
	detail=[stuID,stuname]
	print stuID
	print stuname
	return detail
def video():
	global face_token
	ft=cv2.freetype.createFreeType2()
	ft.loadFontData(fontFileName='./data/font/simhei.ttf',id =0)
	face_cascade = cv2.CascadeClassifier('./data/cascades/haarcascade_frontalface_alt.xml')
	camera=cv2.VideoCapture(0)
	count = 0
	while(True):
		ret,frame=camera.read()
		gray=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
		faces=face_cascade.detectMultiScale(gray,1.3,5)
		GPIO.output(pin_led, GPIO.LOW) ## 关闭 GPIO 引脚（LOW）
		p.start(0)
		for(x,y,w,h) in faces:
			img =cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,255),2)
			if count%5<2:

				f=cv2.resize(gray[y:y+h,x:x+w],(200,200))
				cv2.imwrite('./data/temp/temp.pgm',f)
				result=FaceAPI.searchItoI(image_file='./data/temp/temp.pgm')
				if len(result)==4:
					break			
				if result["results"][0]["confidence"] >= 80.00:
					#print result["results"][0]["confidence"]
					face_token=result["results"][0]["face_token"]
					detail=get_detail()
					# shutil.copyfile("./data/temp/temp.pgm","./data/at/%s/%s.pgm"%(detail,time.strftime('%Y%m%d%H%M%S')))
					print detail
                    			#cv2.putText(img,'WELCOME_312', (x, y - 10), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1.5, (0,0,225), 2)
					#ft.putText(img=img,text=detail[1], org=(x, y - 10), fontHeight=60,line_type=cv2.LINE_AA, color=(0,255,165), thickness=2, bottomLeftOrigin=True)
					#ft.putText(img=img,"hello", org=(x, y - 10), fontHeight=60,line_type=cv2.LINE_AA, color=(0,255,165), thickness=2, bottomLeftOrigin=True)
					#count+=1
				  	#print "*********"
					#print detail[1]
				    	#GPIO.output(pin_led, GPIO.HIGH) ## 打开 GPIO 引脚（HIGH）
					door_open()
 				    
					for i in range(0,10):	#蜂鸣器响五下
						GPIO.output(pin_led,GPIO.HIGH)
						time.sleep(0.02)
						GPIO.output(pin_led,GPIO.LOW)
						time.sleep(0.02)
					time.sleep(1)               ## 等1秒
					door_close()
					#time.sleep(5)
				else:
					print"Unknow face"
					cv2.putText(img,"Unknow", (x, y - 10), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0,0,225), 2)
   					#GPIO.output(pin, GPIO.LOW) ## 关闭 GPIO 引脚（LOW）
					#door_close()
			count +=1
			print count
		cv2.namedWindow("image",cv2.WINDOW_NORMAL)
		cv2.imshow("image",frame)
		if cv2.waitKey(1000 / 12)&0xff==ord("q"):
			break
	camera.release()
	cv2.destroyAllWindows()



if __name__ == '__main__':
	video() 
