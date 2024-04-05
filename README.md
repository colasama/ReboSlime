<!-- markdownlint-disable MD033 MD041 -->
<p align="center">
  <img src="./reboslime.ico" style="border-radius: 100px;" width="200" height="200" alt="Reboslime">
</p>

<div align="center">

# ReboSlime

<!-- prettier-ignore-start -->
<!-- markdownlint-disable-next-line MD036 -->
<div>在 SlimeVR Server 中使用 ReboCap</div>
<div style="margin-bottom: 12px">Use ReboCap in SlimeVR Server</div>

<!-- prettier-ignore-end -->

</div>

<p align="center">
  <a href="https://raw.githubusercontent.com/colasama/reboslime/master/LICENSE">
    <img src="https://img.shields.io/github/license/colasama/reboslime" alt="license">
  </a>
  <img src="https://img.shields.io/badge/python-3.10.x-blue?logo=python&logoColor=edb641" alt="python">
</p>



## 使用说明

- 下载 `Releases` 中的可执行文件，最新 `v0.4.1` 已适配 Rebocap v40 及以后的版本，如果想要使用之前与 VMT 相配合的程序，请下载 `v0.31` 版本。
- 打开 SlimeVR 服务端。
- 打开 ReboCap 客户端，点击 **动作校准1**。
- 运行 `run.bat` 或者 `reboslime.exe`。
- 现在应该能在 SlimeVR 中看到追踪器了！之后按照 SlimeVR 的用法来就可以了。

## 开发相关

- 本项目使用 `Poetry` 进行依赖管理，请安装 3.10.x 版本的 Python 后运行 `pip install poetry`。
- 使用 `poetry install` 安装依赖，然后运行 `poetry run python reboslime.py` 即可运行程序。

## 注意事项

- 由于 ReboCap 客户端自身限制原因，目前必须按照原 VR 使用方法中佩戴胸、腰以及腿部 8 点，并且目前至少佩戴以上 8 个才能正常运行，目前可以在 6 / 8 / 10 / 12 / 15 点中选择。
  - 6 点：胸 + 腰 + 大腿 + 小腿
  - 8 点：胸 + 腰 + 大腿 + 小腿 + 脚
  - 10 点：胸 + 腰 + 大腿 + 小腿 + 脚 + 大臂
  - 12 点：胸 + 腰 + 大腿 + 小腿 + 脚 + 大臂 + 小臂
  - 15 点：全身
- **注意**：目前每一种选择都会出现一个 0 号节点，可以考虑不分配或者分配到 髋部。

## ToDo

- [x] 完成佩戴数量的选择。
- [ ] 解决 15 点模式下头部节点疑似无法使用的问题。

## 感谢

- https://github.com/lmore377/moslime - SlimeVR 网络传输部分，很大程度参考了整个项目的结构
