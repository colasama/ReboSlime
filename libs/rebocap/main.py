import time
from rich.console import Console
import rebocap_ws_sdk

counter = 0
console = Console()

def raw_sdk_example():
    def print_debug_msg(self: rebocap_ws_sdk.RebocapWsSdk, trans, pose24, static_index, ts):
        global counter

        is_left_on_floor = 0 <= static_index <= 5
        is_right_on_floor = 6 <= static_index <= 11
        no_foot_on_ground = static_index < 0
        if counter % 60 == 0:
            print(f'timestamp:{ts}'
                  f'current coordinate_type: {self.coordinate_type.name}'
                  f'root position:{trans} left_on_floor:{is_left_on_floor}  right_on_floor:{is_right_on_floor}')
            for i in range(24):
                print(f'bone:{rebocap_ws_sdk.REBOCAP_JOINT_NAMES[i]} quaternion w,x,y,z is:{pose24[i]}')
            print('\n\n\n\n')
        counter += 1

    # 姿态数据回调
    def pose_msg_callback(self: rebocap_ws_sdk.RebocapWsSdk, tran: list, pose24: list, static_index: int, ts: float):
        for i in range(24):
            console.log(rebocap_ws_sdk.REBOCAP_JOINT_NAMES[i], ["%.5f" % num for num in pose24[i]])
            time.sleep(0.1)


    # 异常断开，这里处理重连或报错
    def exception_close_callback(self: rebocap_ws_sdk.RebocapWsSdk):
        print("exception_close_callback")

    # 初始化sdk
    sdk = rebocap_ws_sdk.RebocapWsSdk(rebocap_ws_sdk.CoordinateType.UECoordinate)
    # 设置姿态回调
    sdk.set_pose_msg_callback(pose_msg_callback)
    # 设置异常断开回调
    sdk.set_exception_close_callback(exception_close_callback)
    # 开始连接
    open_ret = sdk.open(7690)
    # 检查连接状态
    if open_ret == 0:
        print("连接成功")
    else:
        print("连接失败", open_ret)
        if open_ret == 1:
            print("连接状态错误")
        elif open_ret == 2:
            print("连接失败")
        elif open_ret == 3:
            print("认证失败")
        else:
            print("未知错误", open_ret)
        exit(1)
    # 维持启动10秒
    time.sleep(10)
    # 断开连接
    sdk.close()


def main():
    raw_sdk_example()
    pass


if __name__ == "__main__":
    main()
