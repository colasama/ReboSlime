# ReboSlime
> 在 SlimeVR Server 中使用 ReboCap，基于 OSC 协议。 | Use ReboCap in SlimeVR Server based on Open Sound Control protocol.

## 使用说明

- 首先安装 Python 及其依赖 `pip install python-osc`
- 开启 SlimeVR Server 中 OSC 路由功能，并将输入端口设置为 `39570`，输出端口设置为 `39571`。
- 打开 ReboCap 客户端，点击 **动作校准1** 然后点击 VR 校准。
- 运行 `run.bat`。
- 现在应该能在 SlimeVR 中看到追踪器了！之后按照 SlimeVR 的用法来就可以了。

## 注意事项

- 由于 ReboCap 客户端自身限制原因，目前必须按照原 VR 使用方法中佩戴胸、腰以及腿部 6 点，并且目前只能佩戴 8 个，在之后会加入选择佩戴数量的功能。
  - 但是在成功校准后就可以脱掉脚上的追踪器实现只佩戴 6 个追踪器，然后在 SlimeVR 不为该追踪器分配部位即可。

## ToDo

- [ ] 完成佩戴数量的选择

## 感谢

- https://github.com/lmore377/moslime - SlimeVR 网络传输部分，很大程度参考了整个项目的结构
