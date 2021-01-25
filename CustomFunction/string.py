# -*- coding = utf-8 -*-
# @Author: yinzs Wang
# @Time: 2021/1/23 15:14
# @File: string.py
# @Software: PyCharm


def findall(str1, str2):
    '''
    查找一个字符串在另一个字符串出现的所有索引位置
    :param str1: 原字符串
    :param str2: 要查找的字符串
    :return: 返回一个索引列表
    '''
    index = 0
    list = []
    while True:
        index = str1.find(str2, index)
        if index == -1:
            break
        else:
            list.append(index)
            index += 1
    return list
