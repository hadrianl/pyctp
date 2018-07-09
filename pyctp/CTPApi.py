#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/6/27 0027 18:00
# @Author  : Hadrianl 
# @File    : CTPApi.py
# @License : (C) Copyright 2013-2017, 凯瑞投资

from .ctp import  ApiStruct, MdApi, TraderApi
from pyctp.utils import getTempPath, LogInfo, struct_format, dict2bytes, logger
from pyctp.utils import ORDERTYPEDEF as OT

logger.debug('Testing')
class CTPMarket(MdApi):
    def __init__(self):
        super(CTPMarket, self).__init__()
        self.connectionStatus = False
        self.loginStatus = False
        self.reqID = 0
        self.subscribedSymbols = set()

    def connect(self, userID, password, brokerID, address):
        self.userID = userID  # 账号
        self.password = password  # 密码
        self.brokerID = brokerID  # 经纪商代码
        self.address = address  # 服务器地址

        if not self.connectionStatus:
            path = getTempPath(f'CTP_Market_{self.userID}_')
            self.Create(path.encode())

            self.RegisterFront(self.address.encode())

            self.Init()

        else:
            if not self.loginStatus:
                self.login()

    def login(self):
        if self.userID and self.password and self.brokerID:
            req = dict(UserID=self.userID, Password=self.password, BrokerID=self.brokerID)
            req = dict2bytes(req)
            pReqUserLogin = ApiStruct.ReqUserLogin(**req)
            self.reqID += 1
            self.ReqUserLogin(pReqUserLogin, self.reqID)

    def close(self):
        if self.loginStatus:
            UserLogout = ApiStruct.UserLogout()
            UserLogout.BrokerID = self.brokerID.encode()
            UserLogout.UserID = self.userID.encode()
            self.reqID = + 1
            self.ReqUserLogout(UserLogout, self.reqID)
            self.Release()

    def subscribe(self, prodcodes:list):
        if self.loginStatus:
            p_list = [p.encode() for p in prodcodes]
            self.SubscribeMarketData(p_list)
        self.subscribedSymbols.update(prodcodes)

    def register_rsp_callback(self, func_name, log=False):
        if getattr(self, func_name, None) == None:
            logger.error(f'<回调>不存在该回调函数')
            raise Exception(f'<回调>不存在该回调函数')
        def wrapper(handle):
            def handler(pdata, pRspInfo, nRequestID, bIsLast):
                if pdata:
                    d = struct_format(pdata)
                    if log:
                        logger.info(f'<回调处理>信息:{d}')
                    handle(pdata)

                if pRspInfo and pRspInfo.ErrorID != 0:
                    RspInfo = struct_format(pRspInfo)
                    logger.error(f'<ReqID: {nRequestID}>ErrorID:{RspInfo["ErrorID"]}  ErrorMsg:{RspInfo["ErrorMsg"]}')

                if bIsLast:
                    logger.info(f'<回调处理>信息推送完毕')
            setattr(self, func_name, handler)
        return wrapper

    def register_rtn_callback(self, func_name, log=False):
        if getattr(self, func_name, None) == None:
            logger.error(f'<回报>不存在该回报函数')
            raise Exception(f'<回报>不存在该回报函数')
        def wrapper(handle):
            def handler(pdata):
                d = struct_format(pdata)
                if log:
                    logger.info(f'<回报处理>信息:{d}')
                handle(pdata)
            setattr(self, func_name, handler)
        return wrapper

    # def register_errrtn_callback(self, func_name, log=False):
    #     if getattr(self, func_name, None) == None:
    #         logger.error(f'<错误回报>不存在该错误回报函数')
    #         raise Exception(f'<错误回报>不存在该错误回报函数')
    #     def wrapper(handle):
    #         def handler(pdata, pRspInfo):
    #             d = struct_format(pdata)
    #             e = struct_format(pRspInfo)
    #             if log:
    #                 logger.error(f'<错误回报处理>信息:{d}')
    #                 logger.error(f'<错误回报处理>错误:{e}')
    #             handle(pdata)
    #         setattr(self, func_name, handler)
    #     return wrapper

    def OnFrontConnected(self):
        self.connectionStatus = True
        logger.info(LogInfo.M_CONNECTED)
        self.login()

    def OnFrontDisconnected(self, nReason):
        self.connectionStatus = False
        self.loginStatus = False
        logger.info(LogInfo.M_DISCONNECTED)

    def OnHeartBeatWarning(self, nTimeLapse):
        ...

    def OnRspUserLogin(self, pRspUserLogin, pRspInfo, nRequestID, bIsLast):
        if pRspInfo.ErrorID == 0:
            self.loginStatus = True
            RspUserLogin = struct_format(pRspUserLogin)
            logger.info(f'<登入>行情接口：{RspUserLogin["UserID"]}于{RspUserLogin["LoginTime"]}登录成功,当前交易日为{RspUserLogin["TradingDay"]}')

            for s in self.subscribedSymbols:
                self.subcribe(s)

        else:
            RspInfo = struct_format(pRspInfo)
            logger.error(f'<ReqID: {nRequestID}>ErrorID:{RspInfo["ErrorID"]}  ErrorMsg:{RspInfo["ErrorMsg"]}')

    def OnRspUserLogout(self, pUserLogout, pRspInfo, nRequestID, bIsLast):
        if pRspInfo.ErrorID == 0:
            self.loginStatus = False
            UserLogout = struct_format(pUserLogout)
            logger.info(f'<登出>行情接口：{UserLogout["UserID"]} 登出成功')
        else:
            RspInfo = struct_format(pRspInfo)
            logger.error(f'<ReqID: {nRequestID}>ErrorID:{RspInfo["ErrorID"]}  ErrorMsg:{RspInfo["ErrorMsg"]}')

    def OnRspSubMarketData(self, pSpecificInstrument, pRspInfo, nRequestID, bIsLast):
        if pRspInfo.ErrorID == 0:
            self.loginStatus = False
            SpecificInstrument = struct_format(pSpecificInstrument)
            logger.info(f'<订阅>产品:{SpecificInstrument["InstrumentID"]} 订阅成功')
        else:
            RspInfo = struct_format(pRspInfo)
            logger.error(f'<ReqID: {nRequestID}>ErrorID:{RspInfo["ErrorID"]}  ErrorMsg:{RspInfo["ErrorMsg"]}')

    def OnRspUnSubMarketData(self, pSpecificInstrument, pRspInfo, nRequestID, bIsLast):
        if pRspInfo.ErrorID == 0:
            self.loginStatus = False
            SpecificInstrument = struct_format(pSpecificInstrument)
            logger.info(f'<订阅>产品:{SpecificInstrument["InstrumentID"]} 取消订阅成功')
        else:
            RspInfo = struct_format(pRspInfo)
            logger.error(f'<ReqID: {nRequestID}>ErrorID:{RspInfo["ErrorID"]}  ErrorMsg:{RspInfo["ErrorMsg"]}')

    def OnRtnDepthMarketData(self, pDepthMarketData):
        ...

    def OnRspSubForQuoteRsp(self, pSpecificInstrument, pRspInfo, nRequestID, bIsLast):
        ...

    def OnRspUnSubForQuoteRsp(self, pSpecificInstrument, pRspInfo, nRequestID, bIsLast):
        ...

    def OnRtnForQuoteRsp(self, pForQuoteRsp):
        ...

    def OnRspError(self, pRspInfo, nRequestID, bIsLast):
        RspInfo = struct_format(pRspInfo)
        logger.error(f'<ReqID: {nRequestID}>ErrorID:{RspInfo["ErrorID"]}  ErrorMsg:{RspInfo["ErrorMsg"]}')




class CTPTrade(TraderApi):
    def __init__(self):
        super(CTPTrade, self).__init__()
        self.reqID = 0
        self.orderRef = 0

        self.connectionStatus = False  # 连接状态
        self.loginStatus = False  # 登录状态
        self.authStatus = False  # 验证状态
        self.loginFailed = False
        self.requireAuthentication = False


    def connect(self, userID, password, brokerID, address, authCode=None, userProductInfo=None):
        self.userID = userID                # 账号
        self.password = password            # 密码
        self.brokerID = brokerID            # 经纪商代码
        self.address = address              # 服务器地址
        self.authCode = authCode            #验证码
        self.userProductInfo = userProductInfo  #产品信息

        if all([self.authCode, self.userProductInfo]):
            self.requireAuthentication = True

        if not self.connectionStatus:
            path = getTempPath(f'CTP_Trade_{self.userID}_')
            self.Create(path.encode())

            self.SubscribePrivateTopic(0)
            self.SubscribePublicTopic(0)

            self.RegisterFront(self.address.encode())

            self.Init()

        else:
            if self.requireAuthentication and not self.authStatus:
                self.authenticate()
            elif not self.loginStatus:
                self.login()

    def authenticate(self):
        if self.userID and self.brokerID and self.authCode and self.userProductInfo:
            auth_req = ApiStruct.ReqAuthenticate(BrokerID=self.brokerID.encode(),
                                            UserID=self.userID.encode(),
                                            UserProductInfo=self.userProductInfo.encode(),
                                            AuthCode=self.authCode.encode())
            self.reqID += 1
            return self.ReqAuthenticate(auth_req, self.reqID)

    def login(self):
        if self.loginFailed:
            return

        if self.userID and self.password and self.brokerID:
            req = ApiStruct.ReqUserLogin(UserID=self.userID.encode(),
                                         Password=self.password.encode(),
                                         BrokerID=self.brokerID.encode())
            self.reqID += 1
            return self.ReqUserLogin(req, self.reqID)

    def qryOrder(self, instrumentID='', exchangeID='', orderSysID='', startTime='', endTime=''):
        o = ApiStruct.QryOrder(BrokerID=self.brokerID.encode(),
                               InvestorID=self.userID.encode(),
                               InstrumentID=instrumentID.encode(),
                               ExchangeID=exchangeID.encode(),
                               OrderSysID=orderSysID.encode(),
                               InsertTimeStart=startTime.encode(),
                               InsertTimeEnd=endTime.encode()
                               )
        self.reqID += 1
        return self.ReqQryOrder(o, self.reqID)

    def qryTrade(self, instrumentID='', exchangeID='', tradeID='', startTime='', endTime=''):
        t = ApiStruct.QryTrade(BrokerID=self.brokerID.encode(),
                               InvestorID=self.userID.encode(),
                               InstrumentID=instrumentID.encode(),
                               ExchangeID=exchangeID.encode(),
                               TradeID=tradeID.encode(),
                               TradeTimeStart=startTime.encode(),
                               TradeTimeEnd=endTime.encode()
                               )
        self.reqID += 1
        return self.ReqQryTrade(t, self.reqID)

    def qryAccount(self, currencyID=''):
        self.reqID += 1
        tradingAccount = ApiStruct.QryTradingAccount(BrokerID=self.brokerID.encode(), InvestorID=self.userID.encode(), CurrencyID=currencyID.encode())
        return self.ReqQryTradingAccount(tradingAccount, self.reqID)

    def qryPosition(self, instrumentID=''):
        self.reqID += 1
        p = ApiStruct.QryInvestorPosition(BrokerID=self.brokerID.encode(), InvestorID=self.userID.encode(), InstrumentID=instrumentID.encode())
        return self.ReqQryInvestorPosition(p, self.reqID)

    def qryPositionDetail(self, instrumentID=''):
        self.reqID += 1
        p = ApiStruct.QryInvestorPositionDetail(BrokerID=self.brokerID.encode(), InvestorID=self.userID.encode(), InstrumentID=instrumentID.encode())
        return self.ReqQryInvestorPositionDetail(p, self.reqID)

    def qrySettlementInfoConfirm(self):
        self.reqID += 1
        s = ApiStruct.QrySettlementInfoConfirm(BrokerID=self.brokerID.encode(), InvestorID=self.userID.encode())
        self.ReqQrySettlementInfoConfirm(s, self.reqID)
        return self.reqID

    def qrypSettlementInfo(self, date):
        self.reqID += 1
        s = ApiStruct.QrySettlementInfo(BrokerID=self.brokerID.encode(), InvestorID=self.userID.encode(), TradingDay=date.encode())
        return self.ReqQrySettlementInfo(s, self.reqID)

    def qryProduct(self, productID):
        self.reqID += 1
        p = ApiStruct.QryProduct(ProductID=productID.encode())
        return self.ReqQryProduct(p, self.reqID)

    def qryDepthMarketData(self, instrumentID=''):
        self.reqID += 1
        d = ApiStruct.QryDepthMarketData(InstrumentID=instrumentID.encode())
        return self.ReqQryDepthMarketData(d, self.reqID)

    def qryInstrument(self, instrumentID='', exchangeID='', exchangeInstID='', productID=''):
        self.reqID += 1
        i = ApiStruct.QryInstrument(InstrumentID=instrumentID.encode(), ExchangeID=exchangeID.encode(), ExchangeInstID=exchangeInstID.encode(), ProductID=productID.encode())
        return self.ReqQryInstrument(i, self.reqID)

    def qryInstrumentCommissionRate(self, instrumentID=''):
        self.reqID += 1
        rate = ApiStruct.QryInstrumentCommissionRate(BrokerID=self.brokerID.encode(), InvestorID=self.userID.encode(), InstrumentID=instrumentID.encode())
        return self.ReqQryInstrumentCommissionRate(rate, self.reqID)

    def qryTransferBank(self, bankID='', bankBrchID=''):
        self.reqID += 1
        bank = ApiStruct.QryTransferBank(BankID=bankID.encode(), BankBrchID=bankBrchID.encode())
        return self.ReqQryTransferBank(bank, self.reqID)

    def qryMaxOrderVolume(self, brokerID='', investorID='', instrumentID='', direction='0', offsetFlag='0', hedgeFlag='1'):
        self.reqID += 1
        v = ApiStruct.QueryMaxOrderVolume(BrokerID=brokerID.encode(), InvestorID=investorID.encode(),
                                          InstrumentID=instrumentID.encode(), Direction=direction.encode(),
                                          OffsetFlag=offsetFlag.encode(), HedgeFlag=hedgeFlag.encode())
        return self.ReqQueryMaxOrderVolume(v, self.reqID)

    def qryInstrumentMarginRate(self, instrumentID='', investorRange='1', brokerID='', investorID='', hedgeFlag='1'):
        self.reqID += 1
        m = ApiStruct.InstrumentMarginRate(InstrumentID=instrumentID.encode(), InvestorRange=investorRange.encode(),
                                           BrokerID=brokerID.encode(), InvestorID=investorID.encode(), HedgeFlag=hedgeFlag.encode())
        return self.ReqQryInstrumentMarginRate(m, self.reqID)

    def sendOrder(self, order):
        self.reqID += 1
        self.orderRef += 1
        o = ApiStruct.Order()
        dict2bytes(order)
        o.InstrumentID = order['InstrumentID']
        o.LimitPrice = order['LimitPrice']
        o.StopPrice = order.get('StopPrice', 0)
        o.VolumeTotalOriginal = order['Qty']

        o.OrderPriceType = order.get('OrderPriceType', OT.OrderPriceType['LimitPrice'])
        o.Direction = order['Direction']
        o.CombOffsetFlag = order['CombOffsetFlag']

        o.OrderRef = str(self.orderRef).encode()
        o.InvestorID = self.userID.encode()
        o.UserID = self.userID.encode()
        o.BrokerID = self.brokerID.encode()

        o.CombHedgeFlag = order.get('HedgeFlag', OT.HedgeFlag['Speculation'])
        o.ContingentCondition = order.get('ContingentCondition', OT.ContingentCondition['Immediately'])
        o.ForceCloseReason = order.get('ForceCloseReason', OT.ForceCloseReason['NotForceClose'])
        o.IsAutoSuspend = 0
        o.TimeCondition = order.get('TimeCondition', OT.TimeCondition['GFD'])
        o.VolumeCondition = order.get('VolumeCondition', OT.VolumeCondition['Any'])
        o.MinVolume = order.get('MinVolume', 1)
        o.GTDDate = order.get('GTDDate', b'')

        return self.ReqOrderInsert(o, self.reqID)


    def cancelOrder(self, cancelOrderReq):
        self.reqID += 1
        c_o = ApiStruct.InputOrderAction(BrokerID=self.brokerID.encode(),
                                         InvestorID=self.userID.encode(),
                                         InstrumentID=cancelOrderReq['symbol'].encode(),
                                         ExchangeID=cancelOrderReq['ExchangeID'].encode(),
                                         OrderRef=cancelOrderReq['orderId'].encode(),
                                         FrontID=cancelOrderReq['frontId'].encode(),
                                         SessionID=cancelOrderReq['sessionID'].encode(),
                                         ActionFlag=b'0')

        return self.ReqOrderAction(c_o, self.reqID)

    def close(self):
        if self.loginStatus:
            UserLogout = ApiStruct.UserLogout()
            UserLogout.BrokerID = self.brokerID.encode()
            UserLogout.UserID = self.userID.encode()
            self.reqID =+ 1
            self.ReqUserLogout(UserLogout, self.reqID)
            self.Release()

    def register_rsp_callback(self, func_name, log_type='请求回调处理', log=False):
        if getattr(self, func_name, None) == None:
            logger.error(f'<请求回调>不存在该回调函数')
            raise Exception(f'<请求回调>不存在该回调函数')

        def wrapper(handle):
            def handler(pdata, pRspInfo, nRequestID, bIsLast):
                if pdata:
                    d = struct_format(pdata)
                    if log:
                        logger.info(f'<{log_type}>信息:{d}')
                    handle(pdata)

                if pRspInfo and pRspInfo.ErrorID != 0:
                    RspInfo = struct_format(pRspInfo)
                    logger.error(f'<ReqID: {nRequestID}>ErrorID:{RspInfo["ErrorID"]}  ErrorMsg:{RspInfo["ErrorMsg"]}')

                if bIsLast:
                    logger.info(f'<请求回调处理>信息推送完毕')
            setattr(self, func_name, handler)
        return wrapper

    def register_rtn_callback(self, func_name, log_type='回报处理', log=False):
        if getattr(self, func_name, None) == None:
            logger.error(f'<回报>不存在该回报函数')
            raise Exception(f'<回报>不存在该回报函数')
        def wrapper(handle):
            def handler(pdata):
                d = struct_format(pdata)
                if log:
                    logger.info(f'<{log_type}>信息:{d}')
                handle(pdata)
            setattr(self, func_name, handler)
        return wrapper

    def register_errrtn_callback(self, func_name, log=False):
        if getattr(self, func_name, None) == None:
            logger.error(f'<错误回报>不存在该错误回报函数')
            raise Exception(f'<错误回报>不存在该错误回报函数')
        def wrapper(handle):
            def handler(pdata, pRspInfo):
                d = struct_format(pdata)
                e = struct_format(pRspInfo)
                if log:
                    logger.error(f'<错误回报处理>信息:{d}')
                    logger.error(f'<错误回报处理>错误:{e}')
                handle(pdata)
            setattr(self, func_name, handler)
        return wrapper

    def OnFrontConnected(self):
        self.connectionStatus = True

        logger.info(LogInfo.T_CONNECTED)

        if self.requireAuthentication:
            self.authenticate()
        else:
            self.login()

    def OnFrontDisconnected(self, nReason):
        self.connectionStatus = False
        self.loginStatus = False

        logger.info(LogInfo.T_DISCONNECTED)

    def OnHeartBeatWarning(self, nTimeLapse):
        ...

    def OnRspAuthenticate(self, pRspAuthenticate, pRspInfo, nRequestID, bIsLast):
        if pRspInfo.ErrorID == 0:
            self.authStatus = True

            logger.info(LogInfo.T_AUTHENTICATED)

            self.login()
        else:
            RspInfo = struct_format(pRspInfo)
            logger.error(f'<ReqID: {nRequestID}>ErrorID:{RspInfo["ErrorID"]}  ErrorMsg:{RspInfo["ErrorMsg"]}')

    def OnRspUserLogin(self, pRspUserLogin, pRspInfo, nRequestID, bIsLast):
        if pRspInfo.ErrorID == 0:
            RspUserLogin = struct_format(pRspUserLogin)
            self.frontID = RspUserLogin['FrontID']
            self.sessionID = RspUserLogin['SessionID']
            self.loginStatus = True
            logger.info(f'<登入>交易接口：{RspUserLogin["UserID"]}于{RspUserLogin["LoginTime"]}登录成功,当前交易日为{RspUserLogin["TradingDay"]}')

            req = ApiStruct.SettlementInfoConfirm(BrokerID=self.brokerID.encode(), InvestorID=self.userID.encode())
            self.reqID += 1
            self.ReqSettlementInfoConfirm(req, self.reqID)

        else:
            RspInfo = struct_format(pRspInfo)
            logger.error(f'<ReqID: {nRequestID}>ErrorID:{RspInfo["ErrorID"]}  ErrorMsg:{RspInfo["ErrorMsg"]}')

    def OnRspUserLogout(self, pUserLogout, pRspInfo, nRequestID, bIsLast):
        if pRspInfo.ErrorID == 0:
            self.loginStatus = False
            UserLogout = struct_format(pUserLogout)
            logger.info(f'<登出>交易接口：{UserLogout["UserID"]} 登出成功')
        else:
            RspInfo = struct_format(pRspInfo)
            logger.error(f'<ReqID: {nRequestID}>ErrorID:{RspInfo["ErrorID"]}  ErrorMsg:{RspInfo["ErrorMsg"]}')

    def OnRspUserPasswordUpdate(self, pUserPasswordUpdate, pRspInfo, nRequestID, bIsLast):
        if pRspInfo.ErrorID == 0:
            userID = pUserPasswordUpdate.UserID.decode()
            logger.info(f'<密码>账户：{ userID} 修改密码成功')
        else:
            RspInfo = struct_format(pRspInfo)
            logger.error(f'<ReqID: {nRequestID}>ErrorID:{RspInfo["ErrorID"]}  ErrorMsg:{RspInfo["ErrorMsg"]}')

    def OnRspTradingAccountPasswordUpdate(self, pTradingAccountPasswordUpdate, pRspInfo, nRequestID, bIsLast):
        if pRspInfo.ErrorID == 0:
            accID = pTradingAccountPasswordUpdate.AccountID.decode()
            logger.info(f'<密码>账户：{ accID} 修改密码成功')
        else:
            RspInfo = struct_format(pRspInfo)
            logger.error(f'<ReqID: {nRequestID}>ErrorID:{RspInfo["ErrorID"]}  ErrorMsg:{RspInfo["ErrorMsg"]}')

    def OnRspOrderInsert(self, pInputOrder, pRspInfo, nRequestID, bIsLast):
        if pInputOrder:
            order = struct_format(pInputOrder)
            logger.info(f'<订单>报单插入:{order}')

        if pRspInfo and pRspInfo.ErrorID != 0:
            RspInfo = struct_format(pRspInfo)
            logger.error(f'<ReqID: {nRequestID}>ErrorID:{RspInfo["ErrorID"]}  ErrorMsg:{RspInfo["ErrorMsg"]}')

        if bIsLast:
            logger.info(f'<订单>报单插入信息推送完毕')

    def OnRspOrderAction(self, pInputOrderAction, pRspInfo, nRequestID, bIsLast):
        if pInputOrderAction:
            order = struct_format(pInputOrderAction)
            logger.info(f'<订单>报单操作:{order}')

        if pRspInfo and pRspInfo.ErrorID != 0:
            RspInfo = struct_format(pRspInfo)
            logger.error(f'<ReqID: {nRequestID}>ErrorID:{RspInfo["ErrorID"]}  ErrorMsg:{RspInfo["ErrorMsg"]}')

        if bIsLast:
            logger.info(f'<订单>报单操作信息推送完毕')

    def OnRspParkedOrderInsert(self, pParkedOrder, pRspInfo, nRequestID, bIsLast):
        if pParkedOrder:
            order = struct_format(pParkedOrder)
            logger.info(f'<预埋订单>报单插入:{order}')

        if pRspInfo and pRspInfo.ErrorID != 0:
            RspInfo = struct_format(pRspInfo)
            logger.error(f'<ReqID: {nRequestID}>ErrorID:{RspInfo["ErrorID"]}  ErrorMsg:{RspInfo["ErrorMsg"]}')

        if bIsLast:
            logger.info(f'<预埋订单>报单插入信息推送完毕')

    def OnRspParkedOrderAction(self, pParkedOrderAction, pRspInfo, nRequestID, bIsLast):
        if pParkedOrderAction:
            order = struct_format(pParkedOrderAction)
            logger.info(f'<预埋订单>报单操作:{order}')

        if pRspInfo and pRspInfo.ErrorID != 0:
            RspInfo = struct_format(pRspInfo)
            logger.error(f'<ReqID: {nRequestID}>ErrorID:{RspInfo["ErrorID"]}  ErrorMsg:{RspInfo["ErrorMsg"]}')

        if bIsLast:
            logger.info(f'<预埋订单>报单操作信息推送完毕')

    def OnRspQueryMaxOrderVolume(self, pQueryMaxOrderVolume, pRspInfo, nRequestID, bIsLast):
        if pQueryMaxOrderVolume:
            order_volumn = struct_format(pQueryMaxOrderVolume)
            logger.info(f'<订单>最大报单量:{order_volumn}')

        if pRspInfo and pRspInfo.ErrorID != 0:
            RspInfo = struct_format(pRspInfo)
            logger.error(f'<ReqID: {nRequestID}>ErrorID:{RspInfo["ErrorID"]}  ErrorMsg:{RspInfo["ErrorMsg"]}')

        if bIsLast:
            logger.info(f'<订单>最大报单量信息推送完毕')


    def OnRspSettlementInfoConfirm(self, pSettlementInfoConfirm, pRspInfo, nRequestID, bIsLast):
        if pSettlementInfoConfirm:
            settlementInfoConfirm = struct_format(pSettlementInfoConfirm)
            logger.info(f'<结算>信息:{settlementInfoConfirm}')

        if pRspInfo and pRspInfo.ErrorID != 0:
            RspInfo = struct_format(pRspInfo)
            logger.error(f'<ReqID: {nRequestID}>ErrorID:{RspInfo["ErrorID"]}  ErrorMsg:{RspInfo["ErrorMsg"]}')

        if bIsLast:
            logger.info(f'<结算>信息推送完毕')


    def OnRspRemoveParkedOrder(self, pRemoveParkedOrder, pRspInfo, nRequestID, bIsLast):...

    def OnRspRemoveParkedOrderAction(self, pRemoveParkedOrderAction, pRspInfo, nRequestID, bIsLast):...

    def OnRspExecOrderInsert(self, pInputExecOrder, pRspInfo, nRequestID, bIsLast):...

    def OnRspExecOrderAction(self, pInputExecOrderAction, pRspInfo, nRequestID, bIsLast):...

    def OnRspForQuoteInsert(self, pInputForQuote, pRspInfo, nRequestID, bIsLast):...

    def OnRspQuoteInsert(self, pInputQuote, pRspInfo, nRequestID, bIsLast):...

    def OnRspQuoteAction(self, pInputQuoteAction, pRspInfo, nRequestID, bIsLast):...

    def OnRspCombActionInsert(self, pInputCombAction, pRspInfo, nRequestID, bIsLast):...

    def OnRspQryOrder(self, pOrder, pRspInfo, nRequestID, bIsLast):
        if pOrder:
            o = struct_format(pOrder)
            logger.info(f'<订单>订单信息:{o}')

        if pRspInfo and pRspInfo.ErrorID != 0:
            RspInfo = struct_format(pRspInfo)
            logger.error(f'<ReqID: {nRequestID}>ErrorID:{RspInfo["ErrorID"]}  ErrorMsg:{RspInfo["ErrorMsg"]}')

        if bIsLast:
            logger.info(f'<订单>信息推送完毕')

    def OnRspQryTrade(self, pTrade, pRspInfo, nRequestID, bIsLast):
        if pTrade:
            t = struct_format(pTrade)
            logger.info(f'<成交>成交信息:{t}')

        if pRspInfo and pRspInfo.ErrorID != 0:
            RspInfo = struct_format(pRspInfo)
            logger.error(f'<ReqID: {nRequestID}>ErrorID:{RspInfo["ErrorID"]}  ErrorMsg:{RspInfo["ErrorMsg"]}')

        if bIsLast:
            logger.info(f'<成交>信息推送完毕')

    def OnRspQryInvestorPosition(self, pInvestorPosition, pRspInfo, nRequestID, bIsLast):
        if pInvestorPosition:
            p = struct_format(pInvestorPosition)
            logger.info(f'<持仓>持仓信息:{p}')

        if pRspInfo and pRspInfo.ErrorID != 0:
            RspInfo = struct_format(pRspInfo)
            logger.error(f'<ReqID: {nRequestID}>ErrorID:{RspInfo["ErrorID"]}  ErrorMsg:{RspInfo["ErrorMsg"]}')

        if bIsLast:
            logger.info(f'<持仓>信息推送完毕')

    def OnRspQryTradingAccount(self, pTradingAccount, pRspInfo, nRequestID, bIsLast):
        if pTradingAccount:
            t = struct_format(pTradingAccount)
            logger.info(f'<账户>账户信息:{t}')

        if pRspInfo and pRspInfo.ErrorID != 0:
            RspInfo = struct_format(pRspInfo)
            logger.error(f'<ReqID: {nRequestID}>ErrorID:{RspInfo["ErrorID"]}  ErrorMsg:{RspInfo["ErrorMsg"]}')

        if bIsLast:
            logger.info(f'<账户>信息推送完毕')

    def OnRspQryInvestor(self, pInvestor, pRspInfo, nRequestID, bIsLast):...

    def OnRspQryTradingCode(self, pTradingCode, pRspInfo, nRequestID, bIsLast):...

    def OnRspQryInstrumentMarginRate(self, pInstrumentMarginRate, pRspInfo, nRequestID, bIsLast):
        if pInstrumentMarginRate:
            m = struct_format(pInstrumentMarginRate)
            logger.info(f'<保证金率>信息:{m}')

        if pRspInfo and pRspInfo.ErrorID != 0:
            RspInfo = struct_format(pRspInfo)
            logger.error(f'<ReqID: {nRequestID}>ErrorID:{RspInfo["ErrorID"]}  ErrorMsg:{RspInfo["ErrorMsg"]}')

        if bIsLast:
            logger.info(f'<保证金率>信息推送完毕')

    def OnRspQryInstrumentCommissionRate(self, pInstrumentCommissionRate, pRspInfo, nRequestID, bIsLast):
        if pInstrumentCommissionRate:
            t = struct_format(pInstrumentCommissionRate)
            logger.info(f'<手续费>手续费信息:{t}')

        if pRspInfo and pRspInfo.ErrorID != 0:
            RspInfo = struct_format(pRspInfo)
            logger.error(f'<ReqID: {nRequestID}>ErrorID:{RspInfo["ErrorID"]}  ErrorMsg:{RspInfo["ErrorMsg"]}')

        if bIsLast:
            logger.info(f'<手续费>信息推送完毕')

    def OnRspQryExchange(self, pExchange, pRspInfo, nRequestID, bIsLast):...

    def OnRspQryProduct(self, pProduct, pRspInfo, nRequestID, bIsLast):
        if pProduct:
            t = struct_format(pProduct)
            logger.info(f'<产品>产品信息:{t}')

        if pRspInfo and pRspInfo.ErrorID != 0:
            RspInfo = struct_format(pRspInfo)
            logger.error(f'<ReqID: {nRequestID}>ErrorID:{RspInfo["ErrorID"]}  ErrorMsg:{RspInfo["ErrorMsg"]}')

        if bIsLast:
            logger.info(f'<产品>信息推送完毕')

    def OnRspQryInstrument(self, pInstrument, pRspInfo, nRequestID, bIsLast):
        if pInstrument:
            i = struct_format(pInstrument)
            logger.info(f'<合约>合约信息:{i}')

        if pRspInfo and pRspInfo.ErrorID != 0:
            RspInfo = struct_format(pRspInfo)
            logger.error(f'<ReqID: {nRequestID}>ErrorID:{RspInfo["ErrorID"]}  ErrorMsg:{RspInfo["ErrorMsg"]}')

        if bIsLast:
            logger.info('<合约>信息推送完毕')

    def OnRspQryDepthMarketData(self, pDepthMarketData, pRspInfo, nRequestID, bIsLast):
        if pDepthMarketData:
            pSettlementInfo = struct_format(pDepthMarketData)
            logger.info(f'<深度>信息:{pSettlementInfo}')

        if pRspInfo and pRspInfo.ErrorID != 0:
            RspInfo = struct_format(pRspInfo)
            logger.error(f'<ReqID: {nRequestID}>ErrorID:{RspInfo["ErrorID"]}  ErrorMsg:{RspInfo["ErrorMsg"]}')

        if bIsLast:
            logger.info(f'<深度>信息推送完毕')

    def OnRspQrySettlementInfo(self, pSettlementInfo, pRspInfo, nRequestID, bIsLast):
        if pSettlementInfo:
            pSettlementInfo = struct_format(pSettlementInfo)
            logger.info(f'<结算>信息:{pSettlementInfo}')

        if pRspInfo and pRspInfo.ErrorID != 0:
            RspInfo = struct_format(pRspInfo)
            logger.error(f'<ReqID: {nRequestID}>ErrorID:{RspInfo["ErrorID"]}  ErrorMsg:{RspInfo["ErrorMsg"]}')

        if bIsLast:
            logger.info(f'<结算>信息推送完毕')

    def OnRspQrySettlementInfoConfirm(self, pSettlementInfoConfirm, pRspInfo, nRequestID, bIsLast):
        if pSettlementInfoConfirm:
            pSettlementInfo = struct_format(pSettlementInfoConfirm)
            logger.info(f'<结算>信息:{pSettlementInfo}')

        if pRspInfo and pRspInfo.ErrorID != 0:
            RspInfo = struct_format(pRspInfo)
            logger.error(f'<ReqID: {nRequestID}>ErrorID:{RspInfo["ErrorID"]}  ErrorMsg:{RspInfo["ErrorMsg"]}')

        if bIsLast:
            logger.info(f'<结算>信息推送完毕')

    def OnRspQryTransferBank(self, pTransferBank, pRspInfo, nRequestID, bIsLast):
        if pTransferBank:
            transferBank = struct_format(pTransferBank)
            logger.info(f'<转账>信息:{transferBank}')

        if pRspInfo and pRspInfo.ErrorID != 0:
            RspInfo = struct_format(pRspInfo)
            logger.error(f'<ReqID: {nRequestID}>ErrorID:{RspInfo["ErrorID"]}  ErrorMsg:{RspInfo["ErrorMsg"]}')

        if bIsLast:
            logger.info(f'<转账>信息推送完毕')

    def OnRspQryInvestorPositionDetail(self, pInvestorPositionDetail, pRspInfo, nRequestID, bIsLast):
        if pInvestorPositionDetail:
            p = struct_format(pInvestorPositionDetail)
            logger.info(f'<持仓明细>信息:{p}')

        if pRspInfo and pRspInfo.ErrorID != 0:
            RspInfo = struct_format(pRspInfo)
            logger.error(f'<ReqID: {nRequestID}>ErrorID:{RspInfo["ErrorID"]}  ErrorMsg:{RspInfo["ErrorMsg"]}')

        if bIsLast:
            logger.info(f'<持仓明细>信息推送完毕')

    def OnRspQryInvestorPositionCombineDetail(self, pInvestorPositionCombineDetail, pRspInfo, nRequestID, bIsLast):...

    def OnRspQryNotice(self, pNotice, pRspInfo, nRequestID, bIsLast):...

    def OnRspError(self, pRspInfo, nRequestID, bIsLast):
        RspInfo = struct_format(pRspInfo)
        logger.error(f'<ReqID: {nRequestID}>ErrorID:{RspInfo["ErrorID"]}  ErrorMsg:{RspInfo["ErrorMsg"]}')

    def OnRspBatchOrderAction(self, pInputBatchOrderAction, pRspInfo, nRequestID, bIsLast):...

    def OnRspQryAccountregister(self, pAccountregister, pRspInfo, nRequestID, bIsLast):...

    def OnRspFromBankToFutureByFuture(self, pReqTransfer, pRspInfo, nRequestID, bIsLast):...

    def OnRspFromFutureToBankByFuture(self, pReqTransfer, pRspInfo, nRequestID, bIsLast):...

    def OnRspQryBrokerTradingAlgos(self, pBrokerTradingAlgos, pRspInfo, nRequestID, bIsLast):...

    def OnRspQryBrokerTradingParams(self, pBrokerTradingParams, pRspInfo, nRequestID, bIsLast):...

    def OnRspQryCFMMCTradingAccountKey(self, pCFMMCTradingAccountKey, pRspInfo, nRequestID, bIsLast):...

    def OnRspQryCombAction(self, pCombAction, pRspInfo, nRequestID, bIsLast):...

    def OnRspQryCombInstrumentGuard(self, pCombInstrumentGuard, pRspInfo, nRequestID, bIsLast):...

    def OnRspQryContractBank(self, pContractBank, pRspInfo, nRequestID, bIsLast):...

    def OnRspQryEWarrantOffset(self, pEWarrantOffset, pRspInfo, nRequestID, bIsLast):...

    def OnRspQryExchangeMarginRate(self, pExchangeMarginRate, pRspInfo, nRequestID, bIsLast):...

    def OnRspQryExchangeMarginRateAdjust(self, pExchangeMarginRateAdjust, pRspInfo, nRequestID, bIsLast):...

    def OnRspQryExchangeRate(self, pExchangeRate, pRspInfo, nRequestID, bIsLast):...

    def OnRspQryExecOrder(self, pExecOrder, pRspInfo, nRequestID, bIsLast):...

    def OnRspQryForQuote(self, pForQuote, pRspInfo, nRequestID, bIsLast):...
    def OnRspQryInvestorProductGroupMargin(self, pInvestorProductGroupMargin, pRspInfo, nRequestID, bIsLast):...
    def OnRspQryOptionInstrCommRate(self, pOptionInstrCommRate, pRspInfo, nRequestID, bIsLast):...
    def OnRspQryOptionInstrTradeCost(self, pOptionInstrTradeCost, pRspInfo, nRequestID, bIsLast):...
    def OnRspQryParkedOrder(self, pParkedOrder, pRspInfo, nRequestID, bIsLast):...
    def OnRspQryParkedOrderAction(self, pParkedOrderAction, pRspInfo, nRequestID, bIsLast):...
    def OnRspQryProductExchRate(self, pProductExchRate, pRspInfo, nRequestID, bIsLast):...
    def OnRspQryProductGroup(self, pProductGroup, pRspInfo, nRequestID, bIsLast):...
    def OnRspQryQuote(self, pQuote, pRspInfo, nRequestID, bIsLast):...
    def OnRspQrySecAgentACIDMap(self, pSecAgentACIDMap, pRspInfo, nRequestID, bIsLast):...
    def OnRspQryTradingNotice(self, pTradingNotice, pRspInfo, nRequestID, bIsLast):...
    def OnRspQryTransferSerial(self, pTransferSerial, pRspInfo, nRequestID, bIsLast):...
    def OnRspQueryBankAccountMoneyByFuture(self, pReqQueryAccount, pRspInfo, nRequestID, bIsLast):...
    def OnRspQueryCFMMCTradingAccountToken(self, pQueryCFMMCTradingAccountToken, pRspInfo, nRequestID, bIsLast):...

    def OnRtnOrder(self, pOrder):
        o = struct_format(pOrder)
        logger.info(f'<订单>报单回报:{o}')

    def OnRtnTrade(self, pTrade):
        t = struct_format(pTrade)
        logger.info(f'<成交>成交回报:{t}')

    def OnErrRtnOrderInsert(self, pInputOrder, pRspInfo):
        i_o = struct_format(pInputOrder)
        e = struct_format(pRspInfo)
        logger.error(f'<订单>发单错误回报:{i_o} 错误:{e}')

    def OnErrRtnOrderAction(self, pOrderAction, pRspInfo):
        o_a = struct_format(pOrderAction)
        e = struct_format(pRspInfo)
        logger.error(f'<订单>撤单错误回报:{o_a} 错误:{e}')
        

