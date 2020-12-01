from websocket import create_connection, WebSocketTimeoutException, WebSocketConnectionClosedException
from threading import RLock
import requests
import json
import _thread
import time
import zlib
import re
import random
import hashlib

__Threads = []  # 全部存活线程id
AllData = []  # 未解析的data数据
AllMessage = []  # 可以自行调整所有的信息 包括启动 运行时 报错 全部appendstr就行
AllError = []  # 未解析的Error数据
__ThreadsStop = ''  # 线程关闭表示
__lock = RLock()

cmd = ''  # 调用者指令 只是暂时用来判断重连
cmds = {}  # 调用者更多指令

"""
    上传用文件
    作者:ToolsMan_纳米
    文献参考: 
        https://github.com/lovelyyoshino/Bilibili-Live-API/blob/master/API.WebSocket.md

    直接遍历 AllData 就行了
"""

requests.packages.urllib3.disable_warnings()


def __encode(strs, op):
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


def __decode(blob):
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
            formatVar = reg.sub(b'}' + pos.encode() + b'{', shortVar)
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
        raise Exception(e)


def websocket_wss(roomId, threadName=''):
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
    :return
    """
    while cmd != 'disConnect':
        try:
            AllMessage.append(threadName + ':连接中!')
            wss = create_connection('ws://broadcastlv.chat.bilibili.com:2244/sub', timeout=10)
            if wss.status == 101:
                data = {'roomid': roomId,
                        'token': token}
                databy = __encode(json.dumps(data), 7)
                wss.send(databy)
                recv_text = wss.recv()
                joinBackJson = json.loads(__decode(recv_text))
                if joinBackJson['code'] != 0:
                    exit(-1)
                AllMessage.append(threadName + ':连接成功')
                th1 = _thread.start_new_thread(__sendBeat, (wss, "[Thread-sendBeat]"))
                th2 = _thread.start_new_thread(__getMessage, (wss, "[Thread-getMessage]"))
                while 1:
                    if cmd == 'disConnect':
                        AllMessage.append(threadName + ':连接被手动断开')
                        break
                    time.sleep(0.2)  # 加个延迟防止线程多开
                    if len(__Threads) < 2:
                        AllMessage.append(threadName + ':重新连接中')
                        break
                    pass
        except BaseException as msg:
            AllData.clear()
            AllError.append(threadName + ':Fail: ' + str(msg))


def __sendBeat(wss, threadName):
    threadInfo = [threadName]
    __Threads.append(threadInfo)
    while True:
        try:
            databy = __encode('', 2)
            if cmd == 'disConnect':
                break
            wss.send(databy)
            time.sleep(30)
        except ConnectionResetError:
            AllError.append(threadName + ':Exception: ConnectionResetError 链接已断开')
            __Threads.clear()  # 如果发现连接断开
            break
        except WebSocketConnectionClosedException:
            AllError.append(threadName + ':Exception: ConnectionResetError 链接已断开')
            __Threads.clear()  # 如果发现连接断开
            break


def threadDecode(blob, threadName):
    global lists
    try:
        lists = __decode(blob)  # 此处返回的list可能一些公告 心跳回应信息 可以自己print一下看看
    except Exception as e:
        AllError.append('Exception: ' + str(e))
    if lists not in AllData:
        AllData.append(lists)


def __getMessage(wss, threadName):
    threadInfo = [threadName]
    __Threads.append(threadInfo)
    while True:
        try:
            if cmd == 'disConnect':
                break
            recv_date = wss.recv()
            Decodes = _thread.start_new_thread(threadDecode, (recv_date, "[Thread-Decodes]"))  # 为了防止接受阻塞单独开启了一个线程用来分析数据
        except WebSocketTimeoutException as e:
            AllError.append(threadName + ':Exception: WebSocketTimeoutException ' + str(e))
        except BlockingIOError as e:
            AllError.append(threadName + ':Exception: BlockingIOError ' + str(e))
        except WebSocketConnectionClosedException:
            __Threads.clear()
            break


if __name__ == '__main__':
    websocket_wss(22055164)  # 真实房间号
