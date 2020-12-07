# 直播弹幕姬 python核心

作者bilibili ToolsMan_纳米
邮箱 wfprivate@outlook.com


## BDMCNano模块用法 详细用法查看test5.py

模块中对外开放的方法和变量有

   变量: `AllData`,`cmd`
   
   方法: `websocket_wss` 
   
其中 AllDate中存放的是所有b站返回数据 cmd用来传递指令模块内进行判断(目前没有指令)

websocket_wss方法用来启动模块内部的线程 请使用额外的线程启动比如

    _thread.start_new_thread(BDMCNano.websocket_wss, (真实房间号, '线程id'))

并使用下列类似方法获取返回值 下面文本基本与test5.py一致 具体请查看test5.py
    
    import _thread
    import datetime
    import json
    import time
    
    import BDMCNano
    
    
    _thread.start_new_thread(BDMCNano.websocket_wss, (3248451, '1'))
    
    while True:
        time.sleep(0.5)
        for i in BDMCNano.AllData:
            # print(i)
            BDMCNano.AllData.remove(i)
            if type(i) is list:
                if i is not None:
                    for lis in i:
                        danmuInfoJson = json.loads(lis.decode('utf8'))
                        # print(danmuInfoJson)
                        time_now = datetime.datetime.now().strftime('%H点%M分%S秒%f毫秒')  # 当前时间
                        if danmuInfoJson['cmd'] == "DANMU_MSG":  # 具体自己分析一下上面的json 礼物 上舰 超级留言 都在里面了
                            print(time_now + ' : ' + danmuInfoJson['info'][2][1] + "说: " + danmuInfoJson['info'][1])
                        if danmuInfoJson['cmd'] == "INTERACT_WORD":  # 具体自己分析一下上面的json 礼物 上舰 超级留言 都在里面了
                            print(time_now + ' : ' + danmuInfoJson['data']['uname'] + "进入了直播间")
    
            else:
                if i.find(b'ROOM_REAL_TIME_MESSAGE_UPDATE'):
                    pass
                    # 还没写




注意由于没有设计垃圾清除 所有的数据都会存放在`AllData`中,请及时清理 类似上文

    BDMCNano.AllData.remove(i)
    
为了防止cpu占用过高在启动脚本中加入延迟阻塞来减缓cpu的占用

     while True:
        time.sleep(0.5)

如果遇到问题和bug请联系我 或者帮助我!

#### 对外开放的变量与方法
暂未记录


#### 消息类型
1.弹幕类
| 字段 | 说明 |
| --- | --- |
| DANMU_MSG | 弹幕消息 |
| WELCOME_GUARD | 欢迎xxx老爷 |
| ENTRY_EFFECT | 欢迎舰长进入房间 |
| WELCOME |欢迎xxx进入房间 |
|SUPER_CHAT_MESSAGE_JPN | 
|SUPER_CHAT_MESSAGE |二个都是SC留言 |


2.礼物类
| 字段 | 说明 |
| --- | --- |
| SEND_GIFT | 投喂礼物 |
| COMBO_SEND | 连击礼物 |


3.天选之人类
| 字段 | 说明 |
| --- | --- |
| ANCHOR_LOT_START | 天选之人开始完整信息 |
| ANCHOR_LOT_END | 天选之人获奖id |
| ANCHOR_LOT_AWARD| 天选之人获奖完整信息 |


4.上船类
| 字段 | 说明 |
| --- | --- |
| GUARD_BUY   |上舰长
| USER_TOAST_MSG | 续费了舰长
| NOTICE_MSG | 在本房间续费了舰长


5.分区排行类
| 字段 | 说明 |
| --- | --- |
ACTIVITY_BANNER_UPDATE_V2 |小时榜变动


6.关注数变化类
| 字段 | 说明 |
| --- | --- |
ROOM_REAL_TIME_MESSAGE_UPDATE |粉丝关注变动

文献参考: 
        https://github.com/lovelyyoshino/Bilibili-Live-API/blob/master/API.WebSocket.md