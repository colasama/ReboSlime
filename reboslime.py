#!/usr/bin/python3
import json
import socket
import time
import struct
import threading
import os
import argparse
from pythonosc.dispatcher import Dispatcher
from pythonosc import osc_server

CONFIG = json.load(open('config.json'))
VERSION = CONFIG['version']
REBOCAP_COUNT = CONFIG['rebocap_count']
SLIME_IP = CONFIG['slime_ip']  # SlimeVR Server
SLIME_PORT = CONFIG['slime_port']  # SlimeVR Server
TPS = CONFIG['tps']  # SlimeVR packet frequency. Keep below 300 (above 300 has weird behavior)


def build_handshake():
    fw_string = "ReboSlime"
    buffer = b'\x00\x00\x00\x03'  # packet 3 header
    buffer += struct.pack('>Q', PACKET_COUNTER) # packet counter
    buffer += struct.pack('>I', 0) # board ID 
    buffer += struct.pack('>I', 0) # IMU type
    buffer += struct.pack('>I', 0) # MCU type
    buffer += struct.pack('>III', 0, 0, 0) # IMU info
    buffer += struct.pack('>I', 0) # Build
    buffer += struct.pack('B', len(fw_string)) #length of fw string
    buffer += struct.pack(str(len(fw_string)) + 's', fw_string.encode('UTF-8')) #fw string
    buffer += struct.pack('6s', '111111'.encode('UTF-8')) #MAC address (just using a placeholder of 31:31:31:31:31:31 for now)
    buffer += struct.pack('B', 255)
    return buffer


def add_imu(trackerID):
    global PACKET_COUNTER
    buffer = b'\x00\x00\x00\x0f'  # packet 15 header
    buffer += struct.pack('>Q', PACKET_COUNTER) #packet counter
    buffer += struct.pack('B', trackerID) #tracker id (shown as IMU Tracker #x in SlimeVR)
    buffer += struct.pack('B', 0) #sensor status
    buffer += struct.pack('B', 0) #sensor type
    sock.sendto(buffer, (SLIME_IP, SLIME_PORT))
    # print("Add IMU: " + str(trackerID))
    PACKET_COUNTER += 1


def build_rotation_packet(qw: float, qx: float, qy: float, qz: float, tracker_id: int):
    # qw,qx,qy,qz: parts of a quaternion / trackerID: Tracker ID
    buffer = b'\x00\x00\x00\x11'  # packet 17 header
    buffer += struct.pack('>Q', PACKET_COUNTER) #packet counter
    buffer += struct.pack('B', tracker_id) #tracker id (shown as IMU Tracker #x in SlimeVR)
    buffer += struct.pack('B', 1) # data type (use is unknown)
    buffer += struct.pack('>ffff', -qx, qz, qy, qw)  # quaternion as x,z,y,w
    buffer += struct.pack('B', 0) # calibration info (seems to not be used by SlimeVR currently)
    return buffer


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
ZERO_QUAT = [1, 0, 0, 0]
ALL_CONNECTED = False
PACKET_COUNTER = 0

def sendAllIMUs(mac_addrs):  # mac_addrs: Table of mac addresses. Just used to get number of trackers
    global TPS, PACKET_COUNTER
    while True:
        for z in range(TPS):
            for i in range(len(mac_addrs)):
                sensor = globals()['sensor' + str(i) + 'data']
                rot = build_rotation_packet(sensor.qw, sensor.qx, sensor.qy, sensor.qz, i)
                sock.sendto(rot, (SLIME_IP, SLIME_PORT))
                PACKET_COUNTER += 1
                #Accel is not ready yet
                #accel = build_accel_packet(sensor.ax, sensor.ay, sensor.az, i)
                #sock.sendto(accel, (SLIME_IP, SLIME_PORT))
                #PACKET_COUNTER += 1
            #time.sleep(1 / TPS)

def tracker_handler(unused_addr, number, a2, a3, a4, a5, a6, qx, qy, qz, qw):
  global TPS, PACKET_COUNTER
  try:
    rot = build_rotation_packet(qw, qx, qy, qz, number)
    sock.sendto(rot, (SLIME_IP, SLIME_PORT))
    PACKET_COUNTER += 1
  except ValueError: pass

# Main
print("关于节点数目的使用说明：\n\
·  8 点：胸 + 腰 + 大腿 + 小腿 + 脚 \n\
· 10 点：胸 + 腰 + 大腿 + 小腿 + 脚 + 大臂 \n\
· 12 点：胸 + 腰 + 大腿 + 小腿 + 脚 + 大臂 + 小臂 \n\
· 15 点：全身")
REBOCAP_COUNT = input("想要以几点动捕的形式运行呢？（请输入 8 / 10 / 12 / 15）:")

parser = argparse.ArgumentParser()
parser.add_argument("--ip",
    default="127.0.0.1", help="The ip to listen on")
parser.add_argument("--port",
    type=int, default=39570, help="The port to listen on")
args = parser.parse_args()
dispatcher = Dispatcher()
dispatcher.map("/VMT/Room/Driver", tracker_handler)

server = osc_server.ThreadingOSCUDPServer(
    (args.ip, args.port), dispatcher)

# Connected To SlimeVR Server
handshake = build_handshake()
sock.sendto(handshake, (SLIME_IP, SLIME_PORT))
PACKET_COUNTER += 1
print("Handshake with SlimeVR Server Successful!")
time.sleep(.1)

# Add additional IMUs. SlimeVR only supports one "real" tracker per IP so the workaround is to make all the
# trackers appear as extensions of the first tracker.
if int(REBOCAP_COUNT) == 8:
    for i in range(int(REBOCAP_COUNT)):
        for z in range(3): # slimevr has been missing "add IMU" packets so we just send em 3 times to make sure they get thru
            add_imu(i)
        print("Add IMU: " + str(i))
elif int(REBOCAP_COUNT) == 10:
    for i in [0, 1, 2, 3, 4, 5, 6, 7, 9, 10]:
        for z in range(3): # slimevr has been missing "add IMU" packets so we just send em 3 times to make sure they get thru
            add_imu(i)
        print("Add IMU: " + str(i))
elif int(REBOCAP_COUNT) == 12:
    for i in [0, 1, 2, 3, 4, 5, 6, 7, 9, 10, 11, 12]:
        for z in range(3): # slimevr has been missing "add IMU" packets so we just send em 3 times to make sure they get thru
            add_imu(i)
        print("Add IMU: " + str(i))
elif int(REBOCAP_COUNT) == 15:
    for i in range(int(REBOCAP_COUNT)):
        for z in range(3): # slimevr has been missing "add IMU" packets so we just send em 3 times to make sure they get thru
            add_imu(i)
        print("Add IMU: " + str(i))
else:
    print("目前只支持 8 / 10 / 12 / 15 点哦！")
    exit()

time.sleep(.5)
ALL_CONNECTED = True

print("Serving on {}".format(server.server_address))
print("Safe to start tracking. To stop ReboSlime, press Ctrl-C multiple times.")

server.serve_forever()

