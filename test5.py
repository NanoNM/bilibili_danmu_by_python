import _thread
import datetime
import json
import time

import BDMCNano


_thread.start_new_thread(BDMCNano.websocket_wss, (1156962, '[Thread-BDMCNano]'))

while True:
    time.sleep(0.5)
    for i in BDMCNano.AllData:
        # print(i)
        BDMCNano.AllData.remove(i)
        if type(i) is list:
            if i is not None:
                for lis in i:
                    danmuInfoJson = json.loads(lis.decode('utf8'))
                    print(danmuInfoJson)
                    time_now = datetime.datetime.now().strftime('%H:%M:%S.%f')  # 当前时间
                    if danmuInfoJson['cmd'] == "DANMU_MSG":  # 具体自己分析一下上面的json 礼物 上舰 超级留言 都在里面了
                        print(time_now + '  ' + danmuInfoJson['info'][2][1] + "说: " + danmuInfoJson['info'][1])
                    # if danmuInfoJson['cmd'] == "INTERACT_WORD":  # 具体自己分析一下上面的json 礼物 上舰 超级留言 都在里面了
                    #     print(time_now + '  ' + danmuInfoJson['data']['uname'] + "进入了直播间")

        else:
            if i.find(b'ROOM_REAL_TIME_MESSAGE_UPDATE'):
                pass
                # 还没写
