# B08 E7 实验报告：DRAFT 工作流验证与合并门禁

- 姓名／学号：王祎／241250007；轨道：B。
- 仓库：[Delario17/B08-E7](https://github.com/Delario17/B08-E7)。
- 日期与环境：2026-11-06，B08 云服务器，标称 2 GiB，个人服务镜像 `b08-e7-draft:241250007`。
- 基线运行提交：`464bfbfba7dee8a130097c3486cd60209447a954`。
- 个人实验提交：`a0732de641791196b1cb4e94fcad98acdd59587a`。
- 服务器证据根目录：`/root/241250007/B08-E7/work`。

## 1. 验证场景与结果

基线 `e7-mirror-01` 和新增测试后 `e7-student-01` 的完整门禁均通过六项检查。以下证据路径以仓库根目录为基准。

| 场景 | 输入或故障注入 | 预期与实际 | 判定 | 证据 |
|---|---|---|---|---|
| 单元测试 | 个人版本的服务镜像 | 退出 0，25 项通过 | PASS | `work/build-student-01/unit-tests/` |
| 正常修复 | 回放包内候选 | 第一轮退出 1、分类 MISSING_MAKE；第二轮退出 0；程序输出 hello E3、退出 0，SUCCEEDED | PASS | `work/e7-student-01/gate/success/evidence/result.json` |
| 输出不符 | 将预期输出改为错误字符串 | 程序退出 0、输出 hello E3，但 output_matches=false；工作流 FAILED、退出 1 | PASS | `work/e7-student-01/gate/wrong-output/evidence/result.json` |
| 无效候选 | 替换候选 CMD | 构建前拒绝，FAILED、退出 1 | PASS | `work/e7-student-01/gate/invalid-candidate/` |
| 候选构建失败 | 注入 RUN exit 23 | 第一轮捕获 MISSING_MAKE，第二轮退出 1，未进入运行验证；FAILED、退出 1 | PASS | `work/e7-student-01/gate/build-failed/evidence/result.json` |
| 运行超时 | 注入 sleep 10，验证预算 1 秒 | 第二轮构建退出 0，随后 TIMED_OUT、工作流退出 1；清理检查返回 No such container | PASS | `work/e7-student-01/gate/runtime-timeout/` |

正常场景第二轮产出的镜像 ID 为 `sha256:38e317b899e84a0e5ecccacbd05a06d95dd63af14434237b23fe13ef496a6489`，与验证命令最后一个参数一致。整体退出码为 0，结果汇总见 `work/e7-student-01/gate/gate-result.json` 和同目录的 `results.csv`。

两次门禁均采用包内 DeepSeek 候选回放，来源见 `fixtures/ci-candidates/provenance.json`。候选文件 SHA-256 为 `1f94ff0d4cd38463a1a192aa9dd9426ebf848e1793055318052aef156296de5e`，与来源记录一致。B08 将镜像下载地址调整为 DaoCloud，保留基础镜像 digest。

## 2. 个人新增测试

测试位于 `services/draft/tests/test_e7_multistage_241250007.py`。先用单阶段候选验证对照输入能通过，再加入第二条 FROM，断言 `prepare_candidate()` 抛出 `ValueError`，消息包含 `Only single-stage candidates are supported`。该测试直接检查候选校验逻辑。

基线服务测试为 24 项，重建个人镜像后为 25 项，均通过。新增测试单独执行退出 0。证据为 `work/build-mirror-01/unit-tests/stdout.log`、`work/build-student-01/unit-tests/stdout.log` 和 `work/build-student-01/student-test.log`；重建命令与构建输出保存在相应目录的 `build/` 中。

## 3. CI 与合并门禁

| 阶段 | 运行记录 | Head SHA | 结果及产物 |
|---|---|---|---|
| main 正常运行 | [42172923149](https://github.com/Delario17/B08-E7/actions/runs/42172923149) | `38e8d581afc2a92873e82b3be2084bb610e8fa8e` | success；待补下载的 artifact |
| 个人提交正常运行 | [42173141208](https://github.com/Delario17/B08-E7/actions/runs/42173141208) | `a0732de641791196b1cb4e94fcad98acdd59587a` | push 检查 success；待补下载的 artifact |
| 故意失败 | 待补 | 待补 | 待补错误断言日志及 artifact |
| 修复恢复 | 待补 | 待补 | 待补同一 PR 最新提交的通过记录及 artifact |

待补演示 PR 链接、main 保护快照（检查名、App ID、strict、enforce_admins）、普通合并拒绝日志与退出码、OPEN / BLOCKED 快照，以及修复后的 MERGED、mergeCommit 和 mergedAt。云服务器结果和个人提交的正常 CI 已核对，合并门禁演示仍待验收。
