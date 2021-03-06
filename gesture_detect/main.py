# imports - app imports
# import pygr
# import cv2
# import time
# from base import Keycode, Event
# import pyautogui
# if __name__ == '__main__':
#     pad = pygr.PyGR(size = (480, 320), verbose = True)
#     pad.show()
#     while cv2.waitKey(10) not in [Keycode.ESCAPE, Keycode.Q, Keycode.q]:
#         event = pad.get_event()
#         print("Event:", event.type, "Tip:", event.tip)
#         if event.type == Event.FIVE : # 手势五, 向下滚动
#             pyautogui.scroll(-30) # scroll down 10 "clicks"
#         elif event.type == Event.FOUR :# 手势四, 向上滚动
#             pyautogui.scroll(30) # scroll up 10 "clicks"
#         time.sleep(0.1)

import math
import os
import time

import cv2
import numpy as np

from arduino_control.tcp_lib.tcp_client import TcpClient

STABILITY = 10

def _remove_background(img):#去除背景
    fgbg = cv2.createBackgroundSubtractorMOG2() # 利用BackgroundSubtractorMOG2算法消除背景
    fgmask = fgbg.apply(img)
    #cv2.imshow("image2", fgmask)
    kernel = np.ones((3, 3), np.uint8)
    fgmask = cv2.erode(fgmask, kernel, iterations=1)
    res = cv2.bitwise_and(img, img, mask=fgmask)
    return res

def _bodyskin_detetc(frame):#得到去除背景的图片skin
    # 肤色检测: YCrCb之Cr分量 + OTSU二值化
    ycrcb = cv2.cvtColor(frame, cv2.COLOR_BGR2YCrCb) # 分解为YUV图像,得到CR分量
    (_, cr, _) = cv2.split(ycrcb)
    cr1 = cv2.GaussianBlur(cr, (5, 5), 0) # 高斯滤波
    _, skin = cv2.threshold(cr1, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)  # OTSU图像二值化
    cv2.imshow("image1", skin)
    return skin

def _get_contours(array):#得到图片所有的坐标
    contours, hierarchy = cv2.findContours(array, cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    return contours

def _get_eucledian_distance(beg, end):#计算两点之间的坐标
    i=str(beg).split(',')
    j=i[0].split('(')
    x1=int(j[1])
    k=i[1].split(')')
    y1=int(k[0])
    i=str(end).split(',')
    j=i[0].split('(')
    x2=int(j[1])
    k=i[1].split(')')
    y2=int(k[0])
    d=math.sqrt((x1-x2)*(x1-x2)+(y1-y2)*(y1-y2))
    return d

def _get_defects_count(array, contour, defects, verbose = False):
    ndefects = 0
    for i in range(defects.shape[0]):
        s,e,f,_= defects[i,0]
        beg= tuple(contour[s][0])
        end= tuple(contour[e][0])
        far= tuple(contour[f][0])
        a= _get_eucledian_distance(beg, end)
        b= _get_eucledian_distance(beg, far)
        c= _get_eucledian_distance(end, far)
        angle= math.acos((b ** 2 + c ** 2 - a ** 2) / (2 * b * c)) # * 57
        if angle <= math.pi/2 :#90:
            ndefects = ndefects + 1
            if verbose:
                cv2.circle(array, far, 3, 0xFF0000, -1)
                cv2.imshow("image2", array)
        if verbose:
            cv2.line(array, beg, end, 0xFF0000, 1)
            cv2.imshow("image2", array)
    return array, ndefects

def grdetect(array, verbose = False):
    copy = array.copy()
    array = _remove_background(array) # 移除背景, add by wnavy
    thresh = _bodyskin_detetc(array)
    contours = _get_contours(thresh.copy()) # 计算图像的轮廓
    largecont= max(contours, key = lambda contour: cv2.contourArea(contour))
    hull= cv2.convexHull(largecont, returnPoints = False) # 计算轮廓的凸点
    defects= cv2.convexityDefects(largecont, hull) # 计算轮廓的凹点
    res = 0
    if defects is not None:
        # 利用凹陷点坐标, 根据余弦定理计算图像中锐角个数
        copy, ndefects = _get_defects_count(copy, largecont, defects, verbose = verbose)
        # 根据锐角个数判断手势, 会有一定的误差
        if ndefects == 0:
            res = 1
        elif ndefects == 1:
            res = 2
        elif ndefects == 2:
            res = 3
        elif ndefects == 3:
            res = 4
        elif ndefects == 4:
            res = 5
    return res;

def judge(img):
    # imname =  "wif.jpg"
    # img = cv2.imread(imname, cv2.IMREAD_COLOR)
    return grdetect(img, verbose = False)

def game():
    capture = cv2.VideoCapture(0)#打开笔记本的内置摄像头
    cv2.namedWindow("camera",1)
    start_time = time.time()
    # print("给你5秒的时间把手放到方框的位置\n")
    res = 0;
    stability = 0
    while(1):
        ha,img =capture.read()
        #按帧读取视频，ha,img为获取该方法的两个返回值，ha为布尔值，如果读取帧是正确的则返回true
        #如果文件读取到结尾，它的返回值就为false,img就是每一帧的图像，是个三维矩阵
        end_time = time.time()#返回当前时间的时间戳
        cv2.rectangle(img,(426,0),(640,250),(170,170,0))
        #cv2.putText(img,str(int((10-(end_time- start_time)))), (100,100), cv2.FONT_HERSHEY_SIMPLEX, 2, 255)
        #对应参数为图片、添加的文字，左上角图标，字体，字体大小，颜色，即上面一行功能为在图片中显示倒计时
        cv2.imshow("camera",img)
        # if(end_time-start_time>5):#如果时间到达5秒
        #     break
        if(cv2.waitKey(30)>=0):
            break
        ha,img = capture.read()
        cv2.imshow("camera",img)
        img = img[0:210,426:640]
        # cv2.imwrite("wif.jpg",img)
        _res = judge(img)
        if _res == res:
            stability += 1
        elif _res != res and stability < STABILITY:
            stability = 1
            res = _res
        elif _res != res and stability >= STABILITY:
            break
        print(_res, ' ', stability)
    capture.release()
    return res

def main():
    tcp_cli = TcpClient(host='192.168.43.192', port=9999)
    tcp_cli.connect()
    res = 0;
    while(1):
        os.system('cls')#清屏
        res = game()
        if res == 2:
            tcp_cli.send('0')
        if res == 3:
            tcp_cli.send('1')
        if res == 4:
            tcp_cli.send('5')
        elif res == 5:
            tcp_cli.send('4')
        print(res)
    tcp_cli.close()

main()