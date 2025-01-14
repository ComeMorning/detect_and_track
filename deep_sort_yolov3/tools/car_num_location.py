# -*- coding: utf-8 -*-
# 详细介绍：https://blog.csdn.net/weixin_41695564/article/details/79712393
import os
import cv2
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
car_save_path = os.path.join(BASE_DIR, 'data', 'car')
if not os.path.exists(car_save_path):
    os.makedirs(car_save_path)

# 汽车计数
car_num = len(os.listdir(car_save_path))


def preprocess(gray):
    # # 直方图均衡化
    # equ = cv2.equalizeHist(gray)
    # 高斯平滑
    gaussian = cv2.GaussianBlur(gray, (3, 3), 0, 0, cv2.BORDER_DEFAULT)
    # 中值滤波
    median = cv2.medianBlur(gaussian, 5)
    # Sobel算子，X方向求梯度
    sobel = cv2.Sobel(median, cv2.CV_8U, 1, 0, ksize=3)
    # 二值化
    ret, binary = cv2.threshold(sobel, 170, 255, cv2.THRESH_BINARY)
    # 膨胀和腐蚀操作的核函数
    element1 = cv2.getStructuringElement(cv2.MORPH_RECT, (9, 1))
    element2 = cv2.getStructuringElement(cv2.MORPH_RECT, (9, 7))
    # 膨胀一次，让轮廓突出
    dilation = cv2.dilate(binary, element2, iterations=1)
    # 腐蚀一次，去掉细节
    erosion = cv2.erode(dilation, element1, iterations=1)
    # 再次膨胀，让轮廓明显一些
    dilation2 = cv2.dilate(erosion, element2, iterations=3)
    # cv2.imshow('dilation2', dilation2)
    # cv2.waitKey(0)
    return dilation2


def findPlateNumberRegion(img):
    region = []
    # 查找轮廓
    contours, hierarchy = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # list_rate = []
    # 筛选面积小的
    for i in range(len(contours)):
        cnt = contours[i]
        # 计算该轮廓的面积
        area = cv2.contourArea(cnt)

        # 面积小的都筛选掉
        if area < 500:
            continue

        # 找到最小的矩形，该矩形可能有方向
        rect = cv2.minAreaRect(cnt)
        print("rect is:", rect)

        # box是四个点的坐标
        box = cv2.boxPoints(rect)
        box = np.int0(box)

        # 计算高和宽
        height = abs(box[0][1] - box[2][1])
        width = abs(box[0][0] - box[2][0])
        # 车牌正常情况下长高比在2.7-5之间
        ratio = float(width) / float(height)
        print(ratio)
        if ratio > 5 or ratio < 2:
            continue
        # x, y, w, h
        region.append([*box[2], width, height])
    return region


def car_brand_detect(img, save=True):
    global car_num
    if img is None:
        print('Input Error!! 请输入正确路径')
        return []

    # 保存整车图片
    if save:
        cv2.imwrite(os.path.join(car_save_path, str(car_num) + '.jpg'), img)
        car_num += 1
        print('Save Car', car_num)
    # 转化成灰度图
    try:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    except:
        return []

    # 形态学变换的预处理
    dilation = preprocess(gray)

    # 查找车牌区域
    region = findPlateNumberRegion(dilation)

    return region


if __name__ == '__main__':
    imagePath = os.path.join('..', 'data', 'car_pic', '1.jpg')
    img = cv2.imread(imagePath)
    region = car_brand_detect(img, False)
    print(region)
    for box in region:
        cv2.rectangle(img, (box[0], box[1]), (box[0] + box[2], box[1] + box[3]), (0, 255, 0), 2)

    cv2.namedWindow('img', cv2.WINDOW_NORMAL)
    cv2.imshow('img', img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
