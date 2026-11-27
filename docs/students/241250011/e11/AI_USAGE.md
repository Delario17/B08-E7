# E11 AI 使用记录

| 项目 | 记录 |
|---|---|
| 实验人员 | 朱雨乐，241250011，B08，B轨道 |
| 日期 | 2026-11-27 |
| 工具 | Codex 对话助手 |
| 模型版本 | 未记录 |
| 分支 | `student/241250011/e11` |
| 输入准备提交 | `9dae3c89876977dbf04f76f62edb19728dde7ba5` |
| 最终运行源码提交 | `d4753af80175af35d0d9da3f9fc2edd1033a4c91` |
| 实验脚本的模型/API 生成调用 | 无 |

## 输入与辅助内容

向 Codex 提供课程 E11 材料、组长 PR #14、组员 PR #15、本人学号和云服务器操作输出。公共实现以组长 PR #14 的 `e1acb00349a5c3281bf77ff5d61da0ec75ee5f8f` 为基础。

助手整理了分支与 bundle 同步、环境构建、direct/mixed 输入准备、DRAFT 到固定 MD 再到修复和重检的操作流程，并提供个人输入准备脚本、两项测试及报告整理建议。

## 采纳与个人操作

| 内容 | 采用方式 |
|---|---|
| 可重复输入准备 | 使用 `scripts/student_241250011_e11_prepare.py` 创建 direct/mixed 项目、实际 base/target 提交、固定报告、请求和 dataset 来源记录 |
| 网络来源适配 | 缺陷 Dockerfile 与候选使用相同镜像站 Python 标签，候选保留课程 digest；dataset 记录来源与候选 SHA256 |
| mixed 自主任务 | 补齐两个缺失头文件，保留 HEADERS 引用和配方，增加独立测试 |
| 版本拒绝 | 个人测试覆盖外层 commit 过期；真实 DRAFT 运行覆盖内层 data.commit 过期 |
| 故障处理 | OUTPUT_EXISTS 后改用新的 mixed 输出目录，保存成功运行记录 |
| 文档整理 | 提供完整测试与各次终端结果，由助手据此整理个人报告、ADR、接口契约和本记录 |

本人在云服务器执行实验命令，提交输入准备与测试代码，并提供运行结果。公共运行器、候选约束、MakeProfile、版本检查和验证机制沿用组长及课程实现。个人测试文件为 `labs/e11e12/test_student_241250011_e11.py`；其断言方案与输入准备脚本采用助手建议。

## 候选和验证来源

候选由准备脚本按课程安装工具链模式构造，SHA256 为 `771c7c4214a87026da1fe172ed95ff8292f3564b3af6eaf9f3b3f87f1042b9c9`。DRAFT 的 `Manual model response replay` 来源字段标识教学回放流程，本次使用的是固定模式候选。

真实 direct/mixed 运行均先复现 MISSING_MAKE，再成功构建和运行输出 1；补丁验证 accepted=true，最终动态重检无 MISSING。真实内层过期案例返回 STALE_REPORT。

外层过期个人测试以 mock 隔离 DRAFT，验证停止修复和源文件保护。完整测试输出 `Ran 14 tests in 1.316s`、`OK`，退出码 0；其中个人新增 2 项，其余为仓库已有测试。

证据位于 `work/e11-zyl-direct-final-20261127-203636/`、`work/e11-zyl-mixed-20261127-204818-6284/`、`work/e11-zyl-stale-20261127-203636/` 和 `work/e11-zyl-tests-20261127-203636.log`。
