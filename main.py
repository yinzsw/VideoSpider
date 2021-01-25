# -*- coding = utf-8 -*-
# @Author: yinzs Wang
# @Time: 2021/1/23 13:59
# @File: main.py
# @Software: PyCharm
# @SpiderWebSite: http://www.imomoe.ai

import re
import time
import urllib3
import download
import m3u8ToMp4
import CustomFunction.string
from urllib import parse


def main():
    filePath = "D://Videos\\"

    baseSearchUrl = "http://www.imomoe.ai/search.asp?searchword={search}"

    videoDetails = searchVideos(baseSearchUrl)

    videoUrls = getVideoUrls(videoDetails)

    numberList = selector(videoUrls)

    downloader(filePath, videoDetails[1], videoUrls, numberList)


def downloader(filePath, videoName, videoUrls, numberList):
    '''
    视频下载器
    :param filePath: 保存路径 <class 'str'>
    :param videoName: 视频名 <class 'list'>
    :param videoUrls: 视频链接池 <class 'list'>
    :param numberList: 集数列表 <class 'list'>
    :return: None
    '''
    print("\n\n" + time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()) +
          "\n正在下载中,请耐心等待...")

    for number in numberList:
        for videoUrlsLength in range(len(videoUrls)):
            # 异常处理,如果链接失效则尝试下一组
            try:
                print("\n" + "-" * 150)
                fileName = "第%d集" % (number + 1)
                url = videoUrls[videoUrlsLength][number]

                # 获取视频后缀名
                suffix = url[url.rfind("."):]

                if suffix == ".m3u8" or suffix == ".M3U8":
                    m3u8ToMp4.download(url, filePath + videoName + "\\", fileName)
                else:
                    ###################TEST#####################
                    if "http" in url and "https" not in url:  ##
                        url = url.replace("http", "https")  ####
                    download.download(url, filePath + videoName + "\\" + fileName + ".mp4")
            except Exception:
                if videoUrlsLength + 1 != len(videoUrls):
                    print("链接组%d可能存在问题,开始使用链接组%d" % ((videoUrlsLength + 1), (videoUrlsLength + 2)))
                else:
                    print("链接地址可能失效,第%d集未能下载" % (number + 1))
            else:
                break
    return None


def selector(videoUrls):
    '''
    选择下载视频的集数
    global expressions: 下载表达式 <class 'str'>
    :param videoUrls: 视频链接池 <class 'list'>
    :return: 下载集数列表 <class 'list'>
    '''
    videoUrlsLength = len(videoUrls[0])

    numberList = []
    print("\n\n" + time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()) +
          "\n下载帮助:"
          "\n\t不连续单集: 1+4+5 -->下载第1,4,5集"
          "\n\t连续　多集: 50-66 -->下载第50集到第66集"
          "\n\t特殊　用法: -5等同于1-5和1+2+3+4+5  5-同理"
          "\n\t组合　使用: 1+3,5-10,20- -->下载第1集,3集,5-10集和第20集到结束"
          "\n注　　意: 组合使用表达式之间用','(英文逗号)分隔")

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

            indexList1 = CustomFunction.string.findall(expressions, "+")
            indexList2 = CustomFunction.string.findall(expressions, "-")
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


def getVideoUrls(videoDetails):
    '''
    获取视频的链接池
    :param videoDetails: 视频信息列表[url,name] <class 'list'>
    :return: 返回视频链接列表 <class 'list'>
    '''
    print("\n\n" + time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()))
    # 正则表达式规则
    findPlayData = re.compile(r'src="(/playdata.*?)"></script>')
    findPlayUrlList = re.compile(r"',(\['.*?])]")
    findPlayUrl = re.compile(r"\$(.*?)\$")

    # 请求一个链接获取此视频的name和playData.js
    responseHtml = askUrl(videoDetails[0])
    playData = re.findall(findPlayData, responseHtml)[0]
    playDataUrl = 'http://www.imomoe.in' + playData

    # 从js中筛选出playUrlLists
    responseJs = askUrl(playDataUrl)
    playUrlLists = re.findall(findPlayUrlList, responseJs)
    print(videoDetails[1] + "-->共计有%d组下载地址: " % (len(playUrlLists)))
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


def searchVideos(baseSearchUrl):
    '''
    搜索视频
    global responseSearch: 搜索页文件 <class 'str'>
    :param baseSearchUrl: 基础搜索链接 <class 'str'>
    :return: 视频信息列表[url,name] <class 'list'>
    '''
    # 正则表达式规则
    findVideoNames = re.compile(r'<h2>.*?title="(.*?)".*?</h2>')
    findVideoOtherNames = re.compile(r'<span>(别名.*?)</span>')
    findVideoTypes = re.compile(r'</span><span>.*?(类型.*?)</span>')
    findVideoSummaries = re.compile(r'<p>(.*?)</p>')
    findVideoIds = re.compile(r'/view/(\d+).html')

    print(time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()))
    while True:
        # url中文转码
        word = input("输入你想查找视频的名称: ")
        word = parse.quote(word, encoding='gbk', errors='replace')
        searchUrl = baseSearchUrl.format(search=word)
        global responseSearch
        responseSearch = askUrl(searchUrl)

        # 判断输入是否找到记录
        videoOtherNames = re.findall(findVideoOtherNames, responseSearch)
        if not len(videoOtherNames):
            print("对不起，没有找到任何记录! 换个关键字试试?\n")
        else:
            break

    # 查找视频信息
    videoNames = re.findall(findVideoNames, responseSearch)
    videoOtherNames = re.findall(findVideoOtherNames, responseSearch)
    videoTypes = re.findall(findVideoTypes, responseSearch)
    videoSummaries = re.findall(findVideoSummaries, responseSearch)
    videoIds = re.findall(findVideoIds, responseSearch)

    # 显示视频简介
    for index, videoOtherName in enumerate(videoOtherNames):
        print("\n索引：%d" % (index + 1))
        print("名称：" + videoNames[index])
        print(videoOtherName)
        print(videoTypes[index])
        print("简介：" + videoSummaries[index])

    # 输入合法性判断
    print("\n\n" + time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()))
    while True:
        try:
            index = int(input("输入你想查看视频的索引: "))
        except:
            print("--->输入有误, 重新输入!")
        else:
            if 0 < index and index < len(videoOtherNames) + 1:
                videoDetails = []

                id = videoIds[(index - 1) * 2]
                url = f"http://www.imomoe.ai/player/{id}-0-0.html".format(id=id)
                videoDetails.append(url)

                name = videoNames[index - 1]
                videoDetails.append(name)

                print(videoDetails)
                return videoDetails
            else:
                print("--->索引超出范围, 请重新输入!")


def askUrl(url):
    '''
    模拟网页请求
    :param url: 网址 <class 'str'>
    :return: 网页内容 <class 'str'>
    '''
    header = {"User-Agent": "Mozilla/5.0 "}
    http = urllib3.PoolManager()
    response = http.request('GET', url=url, headers=header).data.decode("GBK")
    return response


if __name__ == '__main__':
    main()
