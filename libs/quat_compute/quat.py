import numpy as np
from scipy.spatial.transform import Rotation as R
import json


CONFIG = json.load(open('config.json'))
PARENT_NODE = CONFIG["parent_node"]

def calculate_bone_direction_vector(joint1, joint2):
    """
    计算两个关节之间的方向向量。
    :param joint1: 第一个关节的位置。
    :param joint2: 第二个关节的位置。
    :return: 方向向量。
    """
    direction_vector = np.subtract(joint2, joint1)
    normalized_vector = direction_vector / np.linalg.norm(direction_vector)
    return normalized_vector

def euler_to_quaternion(euler_angles):
    """
    将欧拉角转换为四元数。
    :param euler_angles: 欧拉角，以弧度表示。
    :return: 四元数。
    """
    rotation = R.from_euler('xyz', euler_angles, degrees=False)
    return rotation.as_quat()  # 返回格式为[x, y, z, w]`

def rotvec_to_quaternion(rotvec):
    """
    将旋转向量转换为四元数。
    :param rotvec: 旋转向量
    :return: 对应的四元数
    """
    rotation = R.from_rotvec(rotvec)
    return rotation.as_quat()  # 返回四元数[x, y, z, w]

def compute_global_quaternion(joint_quats):
    """
    计算所有关节的全局四元数。
    :param joint_rotvecs: 关节的旋转向量数组
    :return: 所有关节的全局四元数列表
    """
    num_joints = len(joint_quats)
    global_quats = [np.array([0, 0, 0, 1])] * num_joints  # 初始化全局四元数列表

    for i in range(num_joints):
        local_quat = joint_quats[i]
        parent_idx = PARENT_NODE[i]
        if parent_idx >= 0:  # 如果有父关节
            parent_global_quat = global_quats[parent_idx]
            global_quats[i] = R.from_quat(
                parent_global_quat) * R.from_quat(local_quat)
        else:  # 根关节
            global_quats[i] = local_quat

    return [quat.as_quat() for quat in global_quats]

# # 示例数据：旋转向量和父关节索引
# joint_rotvecs = np.array([[0.1, 0.2, 0.3], [0.1, 0.2, 0.3]])  # 假设旋转向量

# # 计算全局四元数
# global_quats = compute_global_quaternion(joint_rotvecs)
# print(global_quats)
