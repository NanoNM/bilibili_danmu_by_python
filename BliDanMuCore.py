import datetime

import requests
from websocket import create_connection, WebSocketTimeoutException, WebSocketConnectionClosedException
import json
import _thread
import time
import zlib
import re
import random
import hashlib

Threads = []

"""
    上传用文件
    作者:ToolsMan_纳米
    文献参考: 
        https://github.com/lovelyyoshino/Bilibili-Live-API/blob/master/API.WebSocket.md
"""

requests.packages.urllib3.disable_warnings()


def encode(strs, op):
    """
    对发送的数据进行编码
    :param strs: json字符串
    :param op: 操作标记
    """
    packetLen = 16 + len(strs)
    header = [0, 0, 0, 0, 0, 16, 0, 1, 0, 0, 0, op, 0, 0, 0, 1]
    header[3] = packetLen
    for c in strs:
        header.append(int(c.encode().hex(), 16))
    return bytearray(header)


def decode(blob):
    """
    对收到的数据进行解码
    :param blob: 字节码文件
    :return formatVars: 注意此处返回的是字节串数组 并不是字符串数组 方便解码
    :return body.decode('utf-8'): 返回的是json数据 用来判断链接成功
    """
    packetLen = blob[0:4]
    headerLen = blob[4:6]
    ver = blob[6:8]
    op = blob[8:12]
    seq = blob[12:16]
    body = blob[16:]
    if op == b'\x00\x00\x00\x05':
        if body.find(b'\xda') >= 1:  # 判断师傅为zlib压缩
            var = zlib.decompress(body)
            shortVar = var[16:]
            pos = hashlib.md5(str(random.random()).encode(encoding='UTF-8')).hexdigest()
            reg = re.compile(br'}\x00(?:[\s\S]{14})\x00{')
            formatVar = reg.sub(b'}'+pos.encode()+b'{', shortVar)
            formatVars = formatVar.split(pos.encode())
            return formatVars
        else:
            return body
    if op == b'\x00\x00\x00\x08':
        return body.decode('utf-8')
    if op == b'\x00\x00\x00\x03':
        return body
    try:
        pass

    except Exception as e:
        # 如果是心跳回应就会造成异常 不用可以不用管
        print('Exception: ' + str(e) + '; 注意 也可能不是错误')


def websocket_wss(roomId):
    html = requests.session().get(
        "https://api.live.bilibili.com/room/v1/Danmu/getConf?room_id=%s&platform=pc&player=web" % roomId, headers={
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:15.0) Gecko/20100101 Firefox/15.0.1'},
        verify=False, timeout=6).text
    ConfJson = json.loads(html)
    wssUrl = ConfJson['data']['host_server_list'][0]['host']
    token = ConfJson['data']['token']  # 其实上面的步骤并不是必须的
    """
    一定要注意使用真实的房间号 !!!! 真实房间号可以在网页源代码中获取
    :param roomId: 真实房间号
    :return:
    """
    while True:
        try:
            print("connecting!")
            wss = create_connection('ws://broadcastlv.chat.bilibili.com:2244/sub', timeout=10)

            if wss.status == 101:
                data = {'roomid': roomId,
                        'token': token}
                databy = encode(json.dumps(data), 7)
                wss.send(databy)
                recv_text = wss.recv()
                joinBackJson = json.loads(decode(recv_text))
                if joinBackJson['code'] != 0:
                    exit(-1)
                print("connected")
                th1 = _thread.start_new_thread(__sendBeat, (wss, "Thread-1"))
                th2 = _thread.start_new_thread(__getMessage, (wss, "Thread-2"))
                while 1:
                    time.sleep(0.2)  # 加个延迟防止线程多开
                    if len(Threads) < 2:
                        print("reconnecting")
                        break
                    pass
        except BaseException as msg:
            print('Fail: ' + str(msg))


def __sendBeat(wss, threadName):
    threadInfo = [threadName]
    Threads.append(threadInfo)
    while True:
        try:
            databy = encode('', 2)
            wss.send(databy)
            time.sleep(5)
        except ConnectionResetError:
            Threads.clear()  # 如果发现连接断开
            break
        except WebSocketConnectionClosedException:
            Threads.clear()  # 如果发现连接断开
            break


def threadDecode(blob, threadName):
    lists = decode(blob) # 此处返回的list可能一些公告 心跳回应信息 可以自己print一下看看
    if type(lists) is list:
        if lists is not None:
            for lis in lists:
                danmuInfoJson = json.loads(lis.decode('utf8'))
                time_now = datetime.datetime.now().strftime('%H点%M分%S秒%f毫秒')  # 当前时间
                if danmuInfoJson['cmd'] == "DANMU_MSG":  # 具体自己分析一下上面的json 礼物 上舰 超级留言 都在里面了
                    print(time_now + ' : ' + danmuInfoJson['info'][2][1] + "说: " + danmuInfoJson['info'][1])

    else:
        if lists.find(b'ROOM_REAL_TIME_MESSAGE_UPDATE'):
            # 还没写
            pass


def __getMessage(wss, threadName):
    threadInfo = [threadName]
    Threads.append(threadInfo)
    while True:
        try:
            recv_date = wss.recv()
            Decodes = _thread.start_new_thread(threadDecode, (recv_date, "Thread-Decodes"))  # 为了防止接受阻塞单独开启了一个线程用来分析数据
        except WebSocketTimeoutException as e:
            print(e)
        except BlockingIOError as e:
            print(e)
        except WebSocketConnectionClosedException:
            Threads.clear()
            break


if __name__ == '__main__':
    websocket_wss(0000000)  # 真实房间号
