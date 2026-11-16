# E8—E9 AI 使用记录

| 项目 | 记录 |
|---|---|
| 实验人员 | 朱雨乐，241250011，B08，B 轨道 |
| 工具 | Codex 对话助手 |
| 实验脚本的模型 API 调用 | 无 |
| 日期 | 2026-11-12 |
| 对应分支 | `student/241250011/e8-e9` |
| 个人测试提交 | `d9ae358ba6a47cbd4e14e31436faabfc4d42b613` |

## 输入与协助内容

向 Codex 提供了 E8—E10 课程材料路径、B08-E7 仓库、本人的实验分支要求，以及云服务器输出。助手依据 B 组手册和仓库中的 `run_lab.py`、`lab.py`、`test_profile.py`，整理环境构建、E8 固定报告与旧版本拒绝、E9 三种声明风格和副本应用的命令。

云服务器拉取 GitHub 时出现 TLS 终止及 HTTP/2 传输错误。助手核对电脑上 `origin/main` 的 `7737721` 版本，生成 Git bundle，并提供上传、导入与创建 `student/241250011/e8-e9` 的命令。

## 采纳的建议与人工操作

| 建议 | 采用方式 |
|---|---|
| 通过独立样例绑定报告提交 | 使用辅助脚本创建输出目录，执行样例生成、依赖采集和候选补丁检查。 |
| 验证旧报告和未知目标 | E8 运行记录保存 `STALE_REPORT`，个人测试加入 `UNSUPPORTED_TARGET` 和源文件保持断言。 |
| 验证 macro 声明保持 | 在 `apply-demo` 副本应用补丁，并在个人测试中核对变量定义、目标引用及重检的 RD 集合。 |
| 以实际输出整理文档 | 提供运行目录、终端输出、补丁、plan 和 Git 差异，用于整理个人报告、ADR 和本记录。 |

本人在云服务器操作，导入代码并创建个人分支，执行实验命令，将两项测试纳入 `test_profile.py` 并提交。教学核心函数 `fixture()`、`scan()` 与 `patch()` 沿用仓库的参考实现。个人测试代码采用 Codex 给出的方案，代码差异见 `7737721..d9ae358`。

## 实际验证材料

| 项目 | 命令或证据 |
|---|---|
| E8 | `work/e8-B-manual.Bjk6s8/`，包含固定报告、direct 补丁及 `STALE_REPORT`，步骤退出码为 0 |
| E9 | `work/e9-B-manual.ADoOSF/`，包含三种补丁及 `apply-demo/Makefile`，步骤退出码为 0 |
| 个人测试 | `python3 -m unittest discover -s labs/e8e10 -p test_profile.py -v`，两项个人测试均为 `ok`，完整测试 `Ran 11 tests in 0.351s`、`OK`，退出码为 0。日志为 `work/unit-tests-20261112-175023.log` |
| 提交差异 | `git --no-pager diff 7737721..HEAD -- labs/e8e10/lab.py labs/e8e10/test_profile.py` |

首次 E8/E9 使用源码提交 `773772180425b10c7a0c6311612f0874bdca0846`，两次重跑使用 `d9ae358ba6a47cbd4e14e31436faabfc4d42b613`。四次步骤退出码均为 0，镜像 ID 均为 `sha256:b55c300fab85f34399615cb4046f48fab859346d8dedfd3fafad178e0b1c0d5b`。

实验中的补丁由教学程序根据 GCC 依赖采集结果和声明规则生成。Codex 用于操作辅助、测试建议和文档整理。
