# -*- coding: utf-8 -*-

import requests
import json
import re
import os, shutil,time
import urllib.request, urllib.error
from Crypto.Cipher import AES       #注：python3 安装 Crypto 是 pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple pycryptodome
import sys

from PyQt5.QtWidgets import QFileDialog,QMessageBox
import sys
from PyQt5 import QtCore, QtGui, QtWidgets

from . import qt
class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(479, 554)
        self.textout = QtWidgets.QTextBrowser(Form)
        self.textout.setGeometry(QtCore.QRect(20, 191, 431, 331))
        self.textout.setObjectName("textout")
        self.label = QtWidgets.QLabel(Form)
        self.label.setGeometry(QtCore.QRect(180, 10, 101, 31))
        self.label.setObjectName("label")
        self.lujinuot = QtWidgets.QLabel(Form)
        self.lujinuot.setGeometry(QtCore.QRect(90, 60, 271, 20))
        self.lujinuot.setObjectName("lujinuot")
        self.label_3 = QtWidgets.QLabel(Form)
        self.label_3.setGeometry(QtCore.QRect(20, 60, 71, 21))
        self.label_3.setObjectName("label_3")
        self.selectfile = QtWidgets.QPushButton(Form)
        self.selectfile.setGeometry(QtCore.QRect(370, 60, 81, 23))
        self.selectfile.setMouseTracking(False)
        self.selectfile.setTabletTracking(False)
        self.selectfile.setObjectName("selectfile")
        self.startpachong = QtWidgets.QPushButton(Form)
        self.startpachong.setGeometry(QtCore.QRect(20, 140, 431, 41))
        self.startpachong.setObjectName("startpachong")
        self.comboBox = QtWidgets.QComboBox(Form)
        self.comboBox.setGeometry(QtCore.QRect(20, 100, 431, 21))
        self.comboBox.setObjectName("comboBox")
        self.label_2 = QtWidgets.QLabel(Form)
        self.label_2.setGeometry(QtCore.QRect(300, 530, 151, 20))
        self.label_2.setObjectName("label_2")

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "爬虫程序v1.0"))
        self.label.setText(_translate("Form", "<html><head/><body><p><span style=\" font-size:18pt;\">程序设置</span></p></body></html>"))
        self.lujinuot.setText(_translate("Form", "路径显示"))
        self.label_3.setText(_translate("Form", "<html><head/><body><p><span style=\" font-size:12pt;\">文件路径</span></p></body></html>"))
        self.selectfile.setText(_translate("Form", "选择文件"))
        self.startpachong.setText(_translate("Form", "开始爬取"))
        self.label_2.setText(_translate("Form", "作者: 陈   QQ: 283885422"))


def aes_decode(data, key):
    """AES解密
    :param key:  密钥（16.32）一般16的倍数
    :param data:  要解密的数据
    :return:  处理好的数据
    """
    cryptor = AES.new(key,AES.MODE_CBC,key)
    plain_text = cryptor.decrypt(data)
    return plain_text.rstrip(b'\0')   #.decode("utf-8")

def getUrlData(url,DOWNLOAD_PATH):
    """打开并读取网页内容index.m3u8
    :param url: 包含ts文件流的m3u8连接
    :return:  包含TS链接的文件
    """
    try:
        urlData = urllib.request.urlopen(url, timeout=20)  # .read().decode('utf-8', 'ignore')
        return urlData
    except Exception as err:
        error_log = os.path.join(DOWNLOAD_PATH,'error.log')
        with open(error_log,'a+') as f:
            f.write('下载出错 (%s)'%url,err,"\r\n")
        OutWrite('下载出错 (%s)'%url,err)
        return -1

def getDown_reqursts(url,file_path,key):
    """  下载ts视频流
    :param url: ts流链接
    :param file_path: 临时文件路径
    :param key: 加密密钥
    """
    try:
        response = requests.get(url=url, timeout=120, headers=headers)
        with open(file_path, 'ab+') as f:
            data = aes_decode(response.content,key)
            f.write(data)
    except Exception as e:
        OutWrite(e)

def getVideo_requests(url_m3u8,video_Name,key,DOWNLOAD_PATH):
    """ 根据m3u8文件提取出
    :param url_m3u8: 包含ts文件流的m3u8连接
    :param video_Name: 下载的视频名称地址
    :param key: 加密密钥
    """
    OutWrite('>>> 开始下载 ！')
    urlData = getUrlData(url_m3u8,DOWNLOAD_PATH)
    tempName_video = os.path.join(DOWNLOAD_PATH,'%s.ts'%video_Name)  # 创建临时文件
    open(tempName_video, "wb").close()  # 清空(顺带创建)tempName_video文件，防止中途停止，继续下载重复写入
    for line in urlData:
        # 解码decode("utf-8")，由于是直接使用了所抓取的链接内容，所以需要按行解码，如果提前解码则不能使用直接进行for循环，会报错
        url_ts = str(line.decode("utf-8")).strip()  # 重要：strip()，用来清除字符串前后存在的空格符和换行符
        if not '.ts' in url_ts:
            continue
        else:
            if not url_ts.startswith('http'):  # 判断字符串是否以'http'开头，如果不是则说明url链接不完整，需要拼接
                # 拼接ts流视频的url
                url_ts = url_m3u8.replace(url_m3u8.split('/')[-1], url_ts)
        OutWrite(url_ts)
        getDown_reqursts(url_ts,tempName_video,key)
    filename = os.path.join(DOWNLOAD_PATH, '%s.mp4'%video_Name)
    shutil.move(tempName_video, filename)  #转成MP4文件
    OutWrite('>>> %s.mp4 下载完成! '%video_Name)
    # print('>>> %s.mp4 下载完成! '%video_Name)

def run(ret,start_url,DOWNLOAD_PATH):
    """
    :param page: 起始页码
    :param start_url: 起始url
    """
    # OutWrite(ret["list"][0]["detail_link"],"------------",ret["list"][0]["vod_name"])
    for line in ret["list"]:
        url_m3u8 = re.split(r'/',line["vod_pic"])  #取得每一个视频的连接
        num = url_m3u8[3]  #取唯一标识
        url_m3u8 = 'http://rzlkq.com:8091/%s/1000kb/hls/index.m3u8'%num  #拼接视频链接
        video_Name = line["vod_name"]
        key_url = 'http://rzlkq.com:8091/%s/1000kb/hls/key.key'%num #拼接key链接
        key = requests.get(url=key_url,timeout=120,headers=headers).content  #取得key 16位密钥
        getVideo_requests(url_m3u8,video_Name,key,DOWNLOAD_PATH)




def SelectFile():
    #选择保存文件夹
    FileName = QFileDialog.getExistingDirectory()
    ui.lujinuot.setText(FileName)
    # check_dir(FileName)
    DownLoad = FileName
    # DownLoad = re.sub(r'\/','\\',str(FileName))
    OutWrite('文件下载路径：'+FileName)


def OutWrite(msg):
    ui.textout.append(msg)
    QtWidgets.QApplication.processEvents()   #界面实时刷新





def z01():
    # DOWNLOAD_PATH = DownLoad  #下载目录
    DOWNLOAD_PATH = "D:\demo"  #下载目录

    z01page =1
    while True:
        # start_url = "http://qqchub.com/index.php/ajax/data.html?mid=1&page=%s&limit=8&tid=all&by=t&level=1"%z01page
        start_url = "http://www.qqchub88.com/index.php/ajax/data.html?mid=1&page=%s&limit=8&tid=all&by=t&level=1"%z01page
        response = requests.get(url=start_url,headers=headers,timeout=20)
        ret = json.loads(response.text)  #解析json数据
        if not ret["list"]: #列表为空没有数据了就退出
            break
        z01page+=1
        # OutWrite(str(headers))
        start_down(ret,start_url,DOWNLOAD_PATH)


def z02():
    DOWNLOAD_PATH = DownLoad   #下载目录
    z02page =1
    while True:
        start_url = "http://qqchub.com/index.php/ajax/data.html?mid=1&page=%s&limit=8&tid=all&by=t&level=1"%z02page
        response = requests.get(url=start_url,headers=headers,timeout=20)
        ret = json.loads(response.text)  #解析json数据
        if not ret["list"]: #列表为空没有数据了就退出
            break
        z02page+=1
        start_down(ret,start_url,DOWNLOAD_PATH)




def z03():
    DOWNLOAD_PATH = DownLoad  #下载目录
    z03page =1
    while True:
        start_url = "http://qqchub.com/index.php/ajax/data.html?mid=1&page=%s&limit=8&tid=all&by=t&level=1"%z03page
        response = requests.get(url=start_url,headers=headers,timeout=20)
        ret = json.loads(response.text)  #解析json数据
        if not ret["list"]: #列表为空没有数据了就退出
            break
        z03page+=1
        start_down(ret,start_url,DOWNLOAD_PATH)


def z04():
    DOWNLOAD_PATH = DownLoad  #下载目录
    z04page =1
    while True:
        start_url = "http://qqchub.com/index.php/ajax/data.html?mid=1&page=%s&limit=8&tid=all&by=t&level=1"%z04page
        response = requests.get(url=start_url,headers=headers,timeout=20)
        ret = json.loads(response.text)  #解析json数据
        if not ret["list"]: #列表为空没有数据了就退出
            break
        z04page+=1
        start_down(ret,start_url,DOWNLOAD_PATH)



def start_down(ret,start_url,DOWNLOAD_PATH):
    """
    :param page: 起始页码
    :param start_url: 起始url
    """
    # print(ret["list"][0]["detail_link"],"------------",ret["list"][0]["vod_name"])

    for line in ret["list"]:
        url_m3u8 = re.split(r'/',line["vod_pic"])  #取得每一个视频的连接
        num = url_m3u8[3]  #取唯一标识
        url_m3u8 = 'http://rzlkq.com:8091/%s/1000kb/hls/index.m3u8'%num  #拼接视频链接
        video_Name = line["vod_name"]
        key_url = 'http://rzlkq.com:8091/%s/1000kb/hls/key.key'%num #拼接key链接
        key = requests.get(url=key_url,timeout=120,headers=headers).content  #取得key 16位密钥
        getVideo_requests(url_m3u8,video_Name,key,DOWNLOAD_PATH)



def run():
    if str(ui.lujinuot.text()) != "路径显示" and str(ui.lujinuot.text()) != "":
        z01()
    else:
        OutWrite(">>>请先选择下载路径!")
    # ui.textout.append(ui.lujinuot.text())

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_Form()
    ui.setupUi(MainWindow)
    MainWindow.show()


    DownLoad = ""
    headers = {"User-Agent":"Mozilla/5.0 (Linux; Android 8.0.0; MIX 2S Build/OPR1.170623.032) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.84 Mobile Safari/537.36",}



    try:
        ui.selectfile.clicked.connect(SelectFile)
        ui.startpachong.clicked.connect(run)
    except Exception as e:
        OutWrite(e)







    sys.exit(app.exec_())

