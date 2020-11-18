# 直播弹幕姬 python核心

作者bilibili ToolsMan_纳米
邮箱 wfprivate@outlook.com


BDMCNano模块用法

模块中对外开放的方法和变量有

   变量: `AllData`,`cmd`
   
   方法: `websocket_wss` 
   
其中 AllDate中存放的是所有b站返回数据 cmd用来传递指令模块内进行判断(目前没有指令)

websocket_wss方法用来启动模块内部的线程 请使用额外的线程启动比如

    _thread.start_new_thread(BDMCNano.websocket_wss, (真实房间号, '线程id'))

并使用下列类似方法获取返回值
    
    while True:
    for i in BDMCNano.AllData:
        # print(i)

        BDMCNano.AllData.remove(i)
        if type(i) is list:
            if i is not None:
                for lis in i:
                    danmuInfoJson = json.loads(lis.decode('utf8'))
                    time_now = datetime.datetime.now().strftime('%H点%M分%S秒%f毫秒')  # 当前时间
                    if danmuInfoJson['cmd'] == "DANMU_MSG":  # 具体自己分析一下上面的json 礼物 上舰 超级留言 都在里面了
                        print(time_now + ' : ' + danmuInfoJson['info'][2][1] + "说: " + danmuInfoJson['info'][1])

        else:
            if i.find(b'ROOM_REAL_TIME_MESSAGE_UPDATE'):
                # 还没写
                pass



注意由于没有设计垃圾清除 所有的数据都会存放在`AllData`中,请及时清理 类似上文

    BDMCNano.AllData.remove(i)

如果遇到问题和bug请联系我 或者帮助我!

文献参考: 
        https://github.com/lovelyyoshino/Bilibili-Live-API/blob/master/API.WebSocket.md