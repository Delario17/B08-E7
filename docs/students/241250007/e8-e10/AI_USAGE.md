# AI 使用记录

## 工具、日期与使用目的

- 使用工具：Codex 对话助手，具体模型版本未单独记录。
- 日期：2026-11-11。
- 实验人员：王祎，241250007，B08，B 轨道。
- 任务：理解 E8/E9 教学要求、整理执行步骤、补充个人边界测试、定位断线后的会话问题、核对证据并起草文档。

## 输入上下文与建议

向助手提供了 DevOps_E8_E10 材料位置、B08 既有仓库与 Mac／服务器分工，以及本次操作状态。助手读取 B 组手册、参考实现和模板，整理了固定报告生成、commit 检查、Patch、旧报告拒绝及三种声明风格的分步路线。

助手建议新增两项测试：仅包含 REDUNDANT 的报告应生成空补丁；mixed 补丁应用后应保留 HEADERS 定义、变量引用和所有编译配方。对应代码已加入 test_profile.py 的 Student241250007Tests。

SSH 断线后出现 lab_new_run: command not found，助手解释这些函数来自当前 shell 的 source，重新加载 classroom_helpers.sh、调用 lab_ready 即可恢复；已存在的 OUT 通过 work/last-e8-B.path 或 work/last-e9-B.path 读取。新增测试提交后使用新 OUT 重跑，保留此前目录。

根据本人要求，证据下载位置调整到 DevOps 目录下。助手随后读取实际下载的报告、Patch、plan、步骤日志与单测日志，起草本次三份个人文档。

## 采纳内容与人工操作

采纳参考路线的分步操作，使用 RD-only 和 mixed 配方保持测试作为个人贡献。本人完成 Mac 端编辑、Git 提交与推送，服务器端环境构建、样例操作、测试、重跑和证据下载。个人源码提交为 `0dabf6874d06d0940a65e298d93da602aec45e7a`，新增测试 54 行。

教学核心实现来自实验包，`fixture()`、`scan()`、`patch()` 沿用参考代码。个人测试的代码建议来自本次助手交互，由本人纳入仓库并在实际环境验证。文档依据真实日志编写。

## 实际验证记录

| 建议或改动 | 实际验证与结果 |
|---|---|
| RD-only 应生成空补丁 | test_e8_redundant_only_produces_no_patch：ok |
| mixed 保留变量与配方 | test_e9_mixed_patch_preserves_variable_and_recipes：ok |
| 完整测试执行 | unittest discover 原七项加新增两项：Ran 9 tests，OK，退出 0 |
| E8 修改后重跑 | work/e8-B-manual.esj5b0，四步均退出 0 |
| E9 修改后重跑 | work/e9-B-manual.XY6fLu，两步均退出 0 |

测试日志为服务器 `/root/241250007/B08-E7/work/unit-tests-20261111-143813.log`。对应阶段文件、学生源码 SHA、样例 commit 和环境镜像 ID 见个人报告。

## 模型调用与后续记录

E8、E9 的参考程序通过 GCC 依赖采集和规则化文本处理生成补丁，本次运行未配置或调用外部 LLM API。AI 用于操作辅助、测试建议和文档整理；运行结果来自服务器保存的实际证据。E10 的实验和个人 PR 对应 CI 结果在后续完成后另行记录。
