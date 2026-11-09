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

个人阶段在 2026-11-06 完成 25 项测试和六项服务器门禁。全组贡献合入后，2026-11-09 由本人作为组长执行共享门禁演示。个人实验提交 `a0732de641791196b1cb4e94fcad98acdd59587a` 与共享演示提交分别记录。

| 阶段 | 运行记录 | Head SHA | 结论 | 已下载 artifact |
|---|---|---|---|---|
| 全组正常版本 | [42564630236](https://github.com/Delario17/B08-E7/actions/runs/42564630236) | `963b2f4bc883a43b0e12626f368efd9a83874bca` | success | `work/ci-normal/artifacts-42564630236/e7-b-evidence-42564630236-1` |
| 故意失败 | [42568167906](https://github.com/Delario17/B08-E7/actions/runs/42568167906) | `5fa865c2126a53aeec9ec37041bed938dcb84c52` | failure | `work/ci-rejection/artifacts-42568167906/e7-b-evidence-42568167906-1` |
| 同一 PR 修复恢复 | [42568713119](https://github.com/Delario17/B08-E7/actions/runs/42568713119) | `addb1e65fd60e62a9eef55557ce068117a62d8a8` | success | `work/ci-recovery/artifacts-42568713119/e7-b-evidence-42568713119-1` |

本人原个人提交的 [CI 42173141208](https://github.com/Delario17/B08-E7/actions/runs/42173141208) 通过。上表使用全组贡献合入后的正常基线及本次共享演示的三次 artifact，个人服务器测试仍为 25 项；小组正常版本为 28 项，新增演示测试并修复后为 29 项。

共享演示在 [PR #5](https://github.com/Delario17/B08-E7/pull/5) 完成。必需检查为 `e7-b-quality-gate`，App ID 为 `15368`，`strict=true`、`enforce_admins=true`。失败阶段为 `OPEN / BLOCKED`，普通合并退出码为 `1`。修复提交 `addb1e65fd60e62a9eef55557ce068117a62d8a8` 将 version 的预期退出码从 1 改回 0，CI 恢复成功、六项门禁通过；合并前状态为 `OPEN / CLEAN`。

最终 `MERGED`，合并提交为 `9e054d0bde3175e73f6ef1745f2808de853837e6`，合并时间为 2026-11-09 13:44:45（中国标准时间）。完整失败日志、保护快照、PR 状态与恢复记录见仓库根目录的 `work/ci-rejection/`、`work/ci-setup/` 和 `work/ci-recovery/`。

PR 的 head SHA 与 artifact 的实际检出 SHA 分列保存；完整对照及共享验收过程见 `docs/B08-E7合并门禁报告.md`。个人服务器证据仍位于 `/root/241250007/B08-E7/work/e7-student-01`，Mac 保存本次共享 CI 证据。
