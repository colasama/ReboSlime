import random
import enum

from libs.rebocap import rebocap_ws_sdk_ext

REBOCAP_JOINT_NAMES = [
    "Pelvis",
    "L_Hip",
    "R_Hip",
    "Spine1",
    "L_Knee",
    "R_Knee",
    "Spine2",
    "L_Ankle",
    "R_Ankle",
    "Spine3",
    "L_Foot",
    "R_Foot",
    "Neck",
    "L_Collar",
    "R_Collar",
    "Head",
    "L_Shoulder",
    "R_Shoulder",
    "L_Elbow",
    "R_Elbow",
    "L_Wrist",
    "R_Wrist",
    "L_Hand",
    "R_Hand"
]

class CoordinateType(enum.Enum):
    DefaultCoordinate = 0   # x:left y:up z:backward  [right hand coordinate]
    UnityCoordinate = 1
    BlenderCoordinate = 2
    MayaCoordinate = 3
    MaxCoordinate = 4
    UECoordinate = 5


class RebocapWsSdk:
    def __init__(self, coordinate_type: CoordinateType = CoordinateType.DefaultCoordinate):
        self.pose_msg_callback_f = None
        self.exception_close_callback_f = None
        self.coordinate_type: CoordinateType = coordinate_type
        self.handle = rebocap_ws_sdk_ext.rebocap_ws_sdk_new(self, RebocapWsSdk.pose_msg_callback,
                                                            RebocapWsSdk.exception_close_callback,
                                                            coordinate_type.value)

    def __del__(self):
        rebocap_ws_sdk_ext.rebocap_ws_sdk_release(self.handle)

    '''
    set_pose_msg_callback
    设置rebocap姿态回调函数
    回调函数参数:
    - self: RebocapWsSdk
    - tran: float [3]
    - pose24: float [24,3]
    - static_index: int
    - ts: float 秒时间戳
    '''
    def set_pose_msg_callback(self, callback):
        self.pose_msg_callback_f = callback

    '''
    set_exception_close_callback
    设置rebocap异常断开回调函数
    回调函数参数:
    - self: RebocapWsSdk
    '''
    def set_exception_close_callback(self, callback):
        self.exception_close_callback_f = callback

    '''
    open
    连接到rebocap
    参数：
     - port: 连接端口号，对应rebocap软件中配置的数据输出端口
     - uid: 连接用户id，任意正整数均可
     - name: 连接app名，固定填写reborn_app
    返回值：
     - 0: 连接成功
     - 1: 连接状态错误
     - 2: 连接失败
     - 3: 认证失败
    '''
    def open(self, port: int, name="reborn_app", uid=random.randint(0, 9223372036854775807)):
        return rebocap_ws_sdk_ext.rebocap_ws_sdk_open(self.handle, port, name, uid)

    '''
    close
    断开rebocap连接
    '''
    def close(self):
        rebocap_ws_sdk_ext.rebocap_ws_sdk_close(self.handle)

    '''
    pose_msg_callback
    姿态数据回调
    参数
    - tran: [3]
    - pose24: [24,3]
    - static_index: int
    - tp: 毫秒时间戳
    '''
    def pose_msg_callback(self, trans: list, pose24: list, static_index: int, tp: int):
        if self.pose_msg_callback_f is not None:
            self.pose_msg_callback_f(self, trans, pose24, static_index, tp / 1000)

    '''
    exception_close_callback
    异常断开回调，当rebocap连接异常断开时，触发回调此函数
    '''
    def exception_close_callback(self):
        if self.exception_close_callback_f is not None:
            self.exception_close_callback_f(self)

    '''
    get_last_msg
    获取最近一帧的数据
    返回值 tuple(4)
    - tran: [3]
    - pose24: [24,3]
    - static_index: int
    - tp: 毫秒时间戳
    '''
    def get_last_msg(self):
        return rebocap_ws_sdk_ext.rebocap_ws_sdk_get_last_msg(self.handle)
