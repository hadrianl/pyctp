#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/6/27 0027 18:14
# @Author  : Hadrianl 
# @File    : utils.py
# @License : (C) Copyright 2013-2017, 凯瑞投资

import os
import sys
from logging import getLogger, StreamHandler
import logging

handlers = [StreamHandler(sys.stdout)]
_format = "%(asctime)-15s [%(levelname)s] [%(name)s] %(message)s"
_datefmt = "%Y/%m/%d %H:%M:%S"
_level = logging.INFO
logging.basicConfig(
    format=_format, datefmt=_datefmt, level=_level, handlers=handlers)
logger = logging.getLogger('CTP')


def getTempPath(name):
    """获取存放临时文件的路径"""
    tempPath = os.path.join(os.getcwd(), 'temp')
    if not os.path.exists(tempPath):
        os.makedirs(tempPath)

    path = os.path.join(tempPath, name)
    return path


class LogInfo:
    M_CONNECTED = '<连接>行情服务器已成功连接'
    M_DISCONNECTED = '<连接>行情服务器已断开连接'
    T_CONNECTED = '<连接>交易服务器已成功连接'
    T_DISCONNECTED = '<连接>交易服务器已断开连接'
    T_AUTHENTICATED = '<验证>交易服务器已验证'

def struct_format(struct):
    d = dict()
    for n, t in struct._fields_:
        v = getattr(struct, n)
        d[n] = v if not isinstance(v, bytes) else v.decode('GBK')
    return d

def dict2bytes(d):
    for v, k in d.items():
        if isinstance(k, str):
            d[v] = k.encode('GBK')
    return d

class ORDERTYPEDEF:
    Direction = {'Buy': b'0',
                 'Sell': b'1'}

    # 开平仓类型
    OffsetFlag = {'Open': b'0',
                  'Close': b'1',
                  'ForceClose': b'2',
                  'CloseToday': b'3',
                  'CloseYestoday': b'4',
                  'ForceOff': b'5',  # 强减
                  'LocalForceOff': b'6'  # 本地强减
                  }

    # 价格类型
    OrderPriceType = {'AnyPrice': b'1',  # 任意价
                      'LimitPrice': b'2',
                      'BestPrice': b'3',  # 最优价
                      'LastPrice': b'4',
                      'LP+1T': b'5',  # 最新价上浮1个ticks
                      'LP+2T': b'6',
                      'LP+3T': b'7',
                      'AskPrice1': b'8',  # 卖一
                      'AP1+1T': b'9',
                      'AP1+2T': b'A',
                      'AP1+3T': b'B',
                      'BidPrice1': b'C',  # 买一
                      'BP1+1T': b'D',
                      'BP1+2T': b'E',
                      'BP1+3T': b'F',
                      '5LevelPrice': b'G', # 五档价
                      'BestPriceThisSide': b'H'  # 本方最优
                      }

    # 触发条件
    ContingentCondition = {'Immediately': b'1',  # 立即
                           'Touch': b'2',  # 止损
                           'TouchProfit': b'3',  # 止盈
                           'ParkedOrder': b'4',
                           'LP>SP': b'5',  # 最新价大于条件价
                           'LP>=SP': b'6',
                           'LP<SP': b'7',
                           'LP<=SP': b'8',
                           'AP>SP': b'9',
                           'AP>=SP': b'A',  # 卖一价大于等于条件价
                           'AP<SP': b'B',
                           'AP<=SP': b'C',
                           'BP>SP': b'D',
                           'BP>=SP': b'E',
                           'BP<SP': b'F',  # 买一价小于条件价
                           'BP<=SP': b'H'}

    # 成交量条件
    VolumeCondition = {'Any': b'1',
                       'Min': b'2',
                       'All': b'3'}

    # 有效期
    TimeCondition = {'IOC': b'1',  # 立即完成，否则撤销
                     'GFS': b'2',  # 本节有效
                     'GFD': b'3',  # 当日有效
                     'GTD': b'4',  # 指定日期有效
                     'GTC': b'5',  # 撤销前有效
                     'GFA': b'6',  # 集合竞价有效
                     }

    # 投机套保类型
    HedgeFlag = {'Speculation': b'1',
                 'Arbitrage': b'2',
                 'Hedge': b'3',
                 'Covered': b'4',}

    # 强平原因
    ForceCloseReason = {'NotForceClose': b'0',
                        'LackDeposit': b'1',
                        'ClientOverPositionLimit': b'2',
                        'MemberOverPositionLimit': b'3',
                        'NotMultiple': b'4',
                        'Violation': b'5',
                        'Other': b'6',
                        'PersonDeliv': b'7'}