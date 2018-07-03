# CTP封装， 参照vnpy与pyctp的二次封装
-（仅适用于64位win，可以自行编译pyctp的针对相关平台的ctp，替换掉ctp文件夹）
- | 消息 | 格式 | 示例 |
- | 请求 | Req------ | ReqUserLogin |
- | 响应 | OnRsp------ | OnRspUserLogin |
- | 查询 | ReqQry------ | ReqQryInstrument |
- | 查询请求的响应 | OnRspQry------ | OnRspQryInstrument |
- | 回报 | OnRtn------ | OnRtnOrder |
- | 错误回报 | OnErrRtn------ | OnErrRtnOrderInsert |

## MarketAPI
``` python

from pyctp.CTPApi import CTPMarket
market_api = CTPMarket()
market_api.connect('userID', 'password', 'brokerID', 'address')
market_api.subscribe(['IF1807'])
market_api.OnRtnDepthMarketData = lambda data: print(data)  # 简单的处理方式，最好用注册方式实现

@market_api.register_rsp_callback('OnRspSubMarketData', log=True)  # 注册请求回调函数, log为True时会写入日志,默认为False
def onRspSub(data):
    print(data)

@market_api.register_rtn_callback('OnRtnDepthMarketData')  # 注册回报处理函数
def onRtnDepth(data):
    print(data)

```

## TradeAPI
``` python
from pyctp.CTPApi import CTPTrade
trade_api = CTPTrade()
trade_api.connect('userID', 'password', 'brokerID', 'address')

@trade_api.register_rsp_callback('OnRspQryOrder', log=True)  # 注册请求回调函数, log为True时会写入日志,默认为False
def onRspOrder(data):
    print(data)

@trade_api.register_rtn_callback('OnRtnOrder')  # 注册回报处理函数
def onRtnDepth(data):
    print(data)

@trade_api.register_errrtn_callback('OnErrRtnOrderInsert')
def onErrRtnOI(data):
    print(data)

trade_api.qryOrder()
trade_api.qryTrade()
trade_api.qryAccount()
trade_api.qryPosition()
# 查询类的有参数可选，需要处理返回数据的，需要先注册回调函数，默认处理只是用日志输出

# 下单
from pyctp.utils import ORDERTYPEDEF as OT

# 限价单
limit_order = {'InstrumentID': 'IF1808', 'LimitPrice': 3600, 'Qty': 1,
                'OrderPriceType': QT.OrderPriceType['LimitPrice'],
                'Direction': QT.Direction['Buy'], 'CombOffsetFlag': OT.OffsetFlag['Open']}

trade_api.sendOrder(limit_order)

```

## 安装
- python setup.py build
- python setup.py install
