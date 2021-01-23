# -*- coding = utf-8 -*-
# @Author: yinzs Wang
# @Time: 2021/1/23 13:59
# @File: main.py
# @Software: PyCharm
# @SpiderWebSite: http://www.imomoe.ai

import re
import time
import urllib3
import download.download
import custome.string


def main():
    '''
    baseUrl:
        7047: 视频id
        0: 链接组号
        0: 集数
    '''
    baseUrl = "http://www.imomoe.ai/player/7047-0-0.html"

    videoUrls = getVideoUrls(baseUrl)

    videoUrlsLength = len(videoUrls[0])  # 共计集数

    numberList = selector(videoUrlsLength)

    filePath = "D://Videos\\" + videoName

    downloader(videoUrls, numberList, filePath)


def downloader(videoUrls, numberList, filePath):
    '''
    视频下载器
    :param videoUrls: 视频链接池 <class 'list'>
    :param numberList: 集数列表 <class 'list'>
    :param filePath: 保存路径 <class 'str'>
    :return: 0
    '''
    print("\n\n" + time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()) +
          "\n正在下载中,请耐心等待...")

    for number in numberList:
        for videoUrlsLength in range(len(videoUrls)):
            # 异常处理,如果链接失效则尝试下一组
            try:
                print("\n" + "-" * 150)
                url = videoUrls[videoUrlsLength][number]

                # 获取视频后缀名
                suffix = url[url.rfind("."):]

                fileName = "第%d集" % (number + 1)
                download.download(url, filePath + "\\" + fileName + suffix)
            except RuntimeError:
                if videoUrlsLength + 1 != len(videoUrls):
                    print("链接组%d可能存在问题,开始使用链接组%d" % ((videoUrlsLength + 1), (videoUrlsLength + 2)))
                else:
                    print("链接地址可能失效,第%d集未能下载" % (number + 1))
            else:
                break
    return 0


def selector(videoUrlsLength):
    '''
    选择下载视频的集数
    global expressions: 下载表达式
    :param videoUrlsLength: 共计集数 <class 'int'>
    :return: 下载集数列表 <class 'list'>
    '''
    numberList = []
    print("\n\n" + time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()) +
          "\n下载帮助:"
          "\n\t不连续单集: 1+4+5 -->下载第1,4,5集"
          "\n\t连续　多集: 50-66 -->下载第50集到第66集"
          "\n\t特殊　用法: -5等同于1-5和1+2+3+4+5  5-同理"
          "\n\t组合　使用: 1+3,5-10,20- -->下载第1集,3集,5-10集和第20集到结束"
          "\n注　　意: 不允许1-5-10类似冗杂写法或用'+'作为开始或结束")

    # 合法字符列表
    legalChar = [f"{num}" for num in range(10)]
    legalChar.extend(["+", "-", ","])

    # 输入合法性判断
    while True:
        global expressions
        expressions = input("请输入你要下载的集数: ")
        expressions = re.sub(r" |　|\t|\n|\r", "", expressions)  # 去除空白符号

        for char in expressions:
            # 判断包含字符的合法性
            if char not in legalChar:
                print("--->含有非法字符\"%c\", 请重新输入!" % char)
                break
        else:
            # 判断符号"+"与符号"-"的位置合法性

            indexList1 = custome.string.findall(expressions, "+")
            indexList2 = custome.string.findall(expressions, "-")
            indexList1.extend(indexList2)
            for i in indexList1:
                if (i + 1) in indexList1 or (i - 1) in indexList1:
                    print("--->表达式不合法, 请重新输入!")
                    break
            else:
                # 判断数字大小合法性
                numbers = re.findall(r'(\d+)', expressions)
                for number in numbers:
                    if int(number) < 0 or int(number) > videoUrlsLength:
                        print("--->表达式集数超出范围, 请重新输入!")
                        break
                else:
                    confirm = input("按0退出程序, 按1重新录入, 按其他键继续: ")
                    if confirm == "0":
                        exit()
                    elif confirm == "1":
                        continue
                    else:
                        break

    # 表达式集数转列表
    expressions = expressions.split(",")
    for expression in expressions:
        if expression[0] == "-":
            number = re.findall(r'(\d+)', expression)[0]
            number = [f'{j}' for j in range(int(number))]
            numberList.extend(number)

        elif expression[-1] == "-":
            number = re.findall(r'(\d+)', expression)[-1]
            number = [f'{j}' for j in range(int(number) - 1, videoUrlsLength)]
            numberList.extend(number)

        elif "-" not in expression:
            numbers = re.findall(r'(\d+)', expression)
            for number in numbers:
                numberList.append(int(number) - 1)

        else:
            start = re.findall(r'(\d+)', expression)[0]
            end = re.findall(r'(\d+)', expression)[-1]
            number = [f'{j}' for j in range(int(start) - 1, int(end))]
            numberList.extend(number)
    else:
        # list(str)-->list(int)  排序  删重
        numberList = list(map(int, numberList))
        numberList.sort()
        numberList = set(numberList)

    return numberList


def getVideoUrls(baseUrl):
    '''
    获取视频的链接池
    global videoName: 视频名 <class 'str'>
    :param baseUrl: 视频播放详情页的基础链接 <class 'str'>
    :return: 返回视频链接列表 <class 'list'>
    '''
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()))
    # 正则表达式规则
    findVideoName = re.compile(r'<h1>.*?title="(.*?)".*?</h1>')
    findPlayData = re.compile(r'src="(/playdata.*?)"></script>')
    findPlayUrlList = re.compile(r"',(\['.*?])]")
    findPlayUrl = re.compile(r"\$(.*?)\$")

    # 请求一个链接获取此视频的name和playData.js
    responseHtml = askUrl(baseUrl)
    global videoName
    videoName = re.findall(findVideoName, responseHtml)[0]
    playData = re.findall(findPlayData, responseHtml)[0]
    playDataUrl = 'http://www.imomoe.in' + playData

    # 从js中筛选出playUrlLists
    responseJs = askUrl(playDataUrl)
    playUrlLists = re.findall(findPlayUrlList, responseJs)
    print(videoName + "-->共计有%d组下载地址: " % (len(playUrlLists)))
    for index, playUrlStr in enumerate(playUrlLists):
        playUrlList = eval(playUrlStr)
        print("\t第%d组(共%d集): " % ((index + 1), len(playUrlList)), end="")
        print(playUrlList)

    # 清洗链接池,获取可用于下载的链接
    videoUrls = []
    for playUrlStr in playUrlLists:
        playUrlList = re.findall(findPlayUrl, playUrlStr)
        videoUrls.append(playUrlList)

    return videoUrls


def askUrl(url):
    '''
    模拟网页请求
    :param url: 网址 <class 'str'>
    :return: 网页内容 <class 'str'>
    '''
    header = {"User-Agent": "Mozilla/5.0"}
    http = urllib3.PoolManager()
    response = http.request('GET', url=url, headers=header).data.decode("GBK")
    return response


if __name__ == '__main__':
    main()
