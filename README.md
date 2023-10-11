# ReboSlime
> 在 SlimeVR Server 中使用 ReboCap，基于 OSC 协议。 | Use ReboCap in SlimeVR Server based on Open Sound Control protocol.

## 使用说明

- 首先安装 Python 及其依赖 `pip install python-osc`
- 开启 SlimeVR Server 中 OSC 路由功能，并将输入端口设置为 `39570`，输出端口设置为 `39571`。
- 打开 ReboCap 客户端，点击 **动作校准1** 然后点击 VR 校准。
- 运行 `run.bat`。
- 现在应该能在 SlimeVR 中看到追踪器了！之后按照 SlimeVR 的用法来就可以了。

## 注意事项

- 由于 ReboCap 客户端自身限制原因，目前必须按照原 VR 使用方法中佩戴胸、腰以及腿部 8 点，并且目前至少佩戴以上 8 个才能正常运行，目前可以在 8 / 10 / 12 / 15 点中选择。
  - 8 点：胸 + 腰 + 大腿 + 小腿 + 脚
  - 10 点：胸 + 腰 + 大腿 + 小腿 + 脚 + 大臂
  - 12 点：胸 + 腰 + 大腿 + 小腿 + 脚 + 大臂 + 小臂
  - 15 点：全身

- 实现只佩戴 6 个追踪器的方法：在成功校准后，其实就可以脱掉脚上的追踪器放在一边了！在 SlimeVR 中不要为该追踪器分配部位即可。

## ToDo

- [x] 完成佩戴数量的选择。
- [ ] 解决 15 点模式下头部节点疑似无法使用的问题。

## 感谢

- https://github.com/lmore377/moslime - SlimeVR 网络传输部分，很大程度参考了整个项目的结构
