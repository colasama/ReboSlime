import json
import socket
import time
import struct
import signal
from libs.inputimeout import inputimeout, TimeoutOccurred
from libs.rebocap import rebocap_ws_sdk
from rich.console import Console


CONFIG = json.load(open('config.json'))
VERSION = CONFIG['version']
REBOCAP_COUNT = 8
SLIME_IP = CONFIG['slime_ip']  # SlimeVR Server
SLIME_PORT = CONFIG['slime_port']  # SlimeVR Server
# SlimeVR packet frequency. Keep below 300 (above 300 has weird behavior)
TPS = CONFIG['tps']
ZERO_QUAT = [1, 0, 0, 0]
ALL_CONNECTED = False
PACKET_COUNTER = 0
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sdk = rebocap_ws_sdk.RebocapWsSdk(rebocap_ws_sdk.CoordinateType.UECoordinate)

# 姿态数据回调


def pose_msg_callback(self: rebocap_ws_sdk.RebocapWsSdk, tran: list, pose24: list, static_index: int, ts: float):
    for i in range(24):
        if i in CONFIG["imus"][str(REBOCAP_COUNT)]:
            update_imu_quat(i, - pose24[i][0], pose24[i]
                            [1], - pose24[i][2], pose24[i][3])
            if i == 10:
                console.log(rebocap_ws_sdk.REBOCAP_JOINT_NAMES[i], ["%.5f" % num for num in pose24[i]])
            # console.log(rebocap_ws_sdk.REBOCAP_JOINT_NAMES[i], ["%.5f" % num for num in pose24[i]])
            # time.sleep(0.1)


# 异常断开，这里处理重连或报错
def exception_close_callback(self: rebocap_ws_sdk.RebocapWsSdk):
    print("exception_close_callback")


def init_rebocap_ws():
    global sdk
    # 初始化sdk
    # sdk = rebocap_ws_sdk.RebocapWsSdk(rebocap_ws_sdk.CoordinateType.UECoordinate)
    # 设置姿态回调
    sdk.set_pose_msg_callback(pose_msg_callback)
    # 设置异常断开回调
    sdk.set_exception_close_callback(exception_close_callback)
    # 开始连接
    open_ret = sdk.open(7690)
    # 检查连接状态
    if open_ret == 0:
        console.print("Rebocap 客户端连接成功！")
    else:
        console.print("Rebocap 客户端连接失败！", open_ret)
        if open_ret == 1:
            console.print("Rebocap 客户端连接状态错误！")
        elif open_ret == 2:
            console.print("Rebocap 客户端连接失败！")
        elif open_ret == 3:
            console.print("Rebocap 客户端认证失败！")
        else:
            console.print("未知错误！代码：", open_ret)
        exit(1)


def build_handshake():
    fw_string = "ReboSlime"
    buffer = b'\x00\x00\x00\x03'  # packet 3 header
    buffer += struct.pack('>Q', PACKET_COUNTER)  # packet counter
    buffer += struct.pack('>I', 0)  # board ID
    buffer += struct.pack('>I', 0)  # IMU type
    buffer += struct.pack('>I', 0)  # MCU type
    buffer += struct.pack('>III', 0, 0, 0)  # IMU info
    buffer += struct.pack('>I', 0)  # Build
    buffer += struct.pack('B', len(fw_string))  # length of fw string
    buffer += struct.pack(str(len(fw_string)) + 's',
                          fw_string.encode('UTF-8'))  # fw string
    # MAC address (just using a placeholder of 31:31:31:31:31:31 for now)
    buffer += struct.pack('6s', '111111'.encode('UTF-8'))
    buffer += struct.pack('B', 255)
    return buffer


def add_imu(id):
    global PACKET_COUNTER
    buffer = b'\x00\x00\x00\x0f'  # packet 15 header
    buffer += struct.pack('>Q', PACKET_COUNTER)  # packet counter
    # tracker id (shown as IMU Tracker #x in SlimeVR)
    buffer += struct.pack('B', id)
    buffer += struct.pack('B', 0)  # sensor status
    buffer += struct.pack('B', 0)  # sensor type
    sock.sendto(buffer, (SLIME_IP, SLIME_PORT))
    # print("Add IMU: " + str(trackerID))
    PACKET_COUNTER += 1


def add_imus(ids):
    for id in ids:
        # slimevr has been missing "add IMU" packets so we just send em 3 times to make sure they get thru
        for z in range(3):
            add_imu(id)


def build_rotation_packet(qw: float, qx: float, qy: float, qz: float, tracker_id: int):
    # qw,qx,qy,qz: parts of a quaternion / trackerID: Tracker ID
    buffer = b'\x00\x00\x00\x11'  # packet 17 header
    buffer += struct.pack('>Q', PACKET_COUNTER)  # packet counter
    # tracker id (shown as IMU Tracker #x in SlimeVR)
    buffer += struct.pack('B', tracker_id)
    buffer += struct.pack('B', 1)  # data type (use is unknown)
    buffer += struct.pack('>ffff', qx, -qz, qy, qw)  # quaternion as x,z,y,w
    # calibration info (seems to not be used by SlimeVR currently)
    buffer += struct.pack('B', 0)
    return buffer


# mac_addrs: Table of mac addresses. Just used to get number of trackers
def send_all_imus(mac_addrs):
    global TPS, PACKET_COUNTER
    while True:
        for z in range(TPS):
            for i in range(len(mac_addrs)):
                sensor = globals()['sensor' + str(i) + 'data']
                rot = build_rotation_packet(
                    sensor.qw, sensor.qx, sensor.qy, sensor.qz, i)
                sock.sendto(rot, (SLIME_IP, SLIME_PORT))
                PACKET_COUNTER += 1
                # Accel is not ready yet
                # accel = build_accel_packet(sensor.ax, sensor.ay, sensor.az, i)
                # sock.sendto(accel, (SLIME_IP, SLIME_PORT))
                # PACKET_COUNTER += 1
            # time.sleep(1 / TPS)


def update_imu_quat(id, qx, qy, qz, qw):
    global TPS, PACKET_COUNTER
    try:
        rot = build_rotation_packet(qw, qx, qy, qz, id)
        sock.sendto(rot, (SLIME_IP, SLIME_PORT))
        PACKET_COUNTER += 1
    except ValueError:
        pass

# Main
console = Console()
console.print(" ___       _          ___  _  _             \n\
| _ \ ___ | |__  ___ / __|| |(_) _ __   ___ \n\
|   // -_)|  _ \/ _ \\\__ \| || || '  \ / -_)\n\
|_|_\\\___||____/\___/|___/|_||_||_|_|_|\___|  v" + VERSION + "\n\
")
console.print("关于节点数目的使用说明：\n\
· 6  点：胸部 + 髋部 + 大腿 + 小腿 \n\
· 8  点：胸 + 腰 + 大腿 + 小腿 + 脚 \n\
· 10 点：胸 + 腰 + 大腿 + 小腿 + 脚 + 大臂 \n\
· 12 点：胸 + 腰 + 大腿 + 小腿 + 脚 + 大臂 + 小臂 \n\
· 15 点：全身\n")

try:
    REBOCAP_COUNT = inputimeout(
        "想要以几点动捕的形式运行呢？如无输入，将在 10 秒后以 8 点模式运行（请输入 6 / 8 / 10 / 12 / 15）: ", 10)
except TimeoutOccurred:
    REBOCAP_COUNT = 8

# 连接 Rebocap
init_rebocap_ws()

# Connected To SlimeVR Server
handshake = build_handshake()
sock.sendto(handshake, (SLIME_IP, SLIME_PORT))
PACKET_COUNTER += 1
console.print("成功连接到 SlimeVR 服务器!")
time.sleep(0.1)

# Add additional IMUs. SlimeVR only supports one "real" tracker per IP so the workaround is to make all the
# trackers appear as extensions of the first tracker.
if int(REBOCAP_COUNT) in (6, 8, 10, 12, 15):
    imus = CONFIG['imus'][str(REBOCAP_COUNT)]
    add_imus(imus)
    console.print("Add IMUs: " + str(imus))
else:
    console.print("目前只支持 6 / 8 / 10 / 12 / 15 点哦！")
    exit()

time.sleep(.5)
ALL_CONNECTED = True

console.print("已开启追踪！如果想要停止 ReboSlime, 多按几次 Ctrl-C 即可。")

try:
    # TODO: 优雅地等待
    time.sleep(1000000)
except KeyboardInterrupt:
    sdk.close()
