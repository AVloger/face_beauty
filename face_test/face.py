from aip import AipFace
import base64
import cv2
import time
import signal
import atexit


APP_ID = '15528557'
API_KEY = '0lWqcU5h1MrGzvbnUYXp1vSF'
SECRET_KEY = 'UYknUWhFGqk8YvCzbhD1Wv9e8gza2zuX '
 
aipFace = AipFace(APP_ID, API_KEY, SECRET_KEY)
filePath = 'temp.png'
def get_file_content(filePath):
    with open(filePath, 'rb') as fp:
        content = base64.b64encode(fp.read())
        return content.decode('utf-8')

#filePath = r'./data/temp/temp.pgm'
camera=cv2.VideoCapture(0) #捕抓照片
while(True):
    ret,frame=camera.read()
    cv2.imwrite('temp.png',frame)

    imageType = "BASE64"
        
    options = {}
    options["face_field"] = "age,gender,beauty"

    result = aipFace.detect(get_file_content(filePath),imageType,options)
    print(result)
    cv2.namedWindow("image",cv2.WINDOW_NORMAL)
    cv2.imshow("image",frame)
    if cv2.waitKey(1000 // 12)&0xff==ord("q"):
        break
camera.release()
cv2.destroyAllWindows()



# img = cv2.imread(filePath)

# height,width = img.shape[:2]  #获取原图像的水平方向尺寸和垂直方向尺寸。
# res = cv2.resize(img,(500,500),interpolation=cv2.INTER_CUBIC)

# cv2.imshow('res', res)
# cv2.waitKey(0)
 
