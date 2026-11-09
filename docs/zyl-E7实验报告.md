# B08 E7 实验报告：DRAFT 工作流与故障验证

| 项目 | 记录 |
|---|---|
| 姓名／学号／轨道 | 朱雨乐／241250011／B |
| 仓库 | [Delario17/B08-E7](https://github.com/Delario17/B08-E7) |
| 个人分支 | `student/241250011/e7` |
| 实验源码提交 | `473e0adcbeb72b02b4beea3f5cbcd583243f195d` |
| 门禁开始时间 | 2026-11-08 03:00:53.996735（UTC+8）；入口记录为 `2026-11-07T19:00:53.996735+00:00` |
| 服务器仓库 | `/root/241250011/B08-E7` |
| 个人服务镜像 | `b08-e7-draft:241250011` |
| 修改前构建目录 | `work/build-e7-zyl-before-20261108-025607` |
| 修改后构建目录 | `work/build-e7-zyl-after-20261108-025607` |
| 完整门禁目录 | `work/e7-zyl-20261108-025607` |

## 1. 环境与候选来源

环境自检记录为 Ubuntu 22.04.5 LTS、x86_64、2 CPU、1.7 GiB 内存、64.6 GiB 可用磁盘。工具版本为 Docker 29.1.3、Compose 2.40.3+ds1-0ubuntu1~22.04.1、Buildx 0.30.1、Git 2.34.1、GNU Make 4.3 和 Python 3.10.12。

本次复用本人 E5 选择的 `error-02`，输入位于 `inputs/zyl-error-02/Dockerfile`，来源材料为同目录的 `README.md` 和 `e5-provenance.json`。E5 来源记录的平台为 DeepSeek，模型版本按当时记录为 DeepSeek V4.1 Flash，日期为 2026-11-01。候选在固定基础镜像和原有项目指令之间增加 `build-essential` 安装步骤，并清理 apt 索引。

原始输入候选及正常场景候选的 SHA-256 一致：

```text
92d1cb0b766427c2d598a0641f03b2e04bc702bfb3e9d7bda4541fd88b17d92c
```

入口 `invocation.json` 记录 `track=B`、`stage=gate`、`replay=false`，对应显式传入本人候选。核心结果中的 `DRAFT_TEACHING_REPLAY` 描述执行已保存候选的机制，本次没有调用模型 API。

## 2. 个人扩展测试与服务测试

新增测试位于 `services/draft/tests/test_student_241250011_e7.py`，检查镜像 inspect 失败后的终止条件。测试示例来源为助手辅助。

测试通过受控 Docker 响应，使第一轮构建返回缺少 make、第二轮构建返回成功，随后让 `docker image inspect` 返回失败。预期工作流状态为 `FAILED`，错误为 `Cannot inspect built image`，两轮构建退出码依次为 `[1, 0]`，且不执行程序运行命令、不生成 `verification` 字段。测试还核对保存的 `result.json` 和 inspect 标准错误日志。

这项单元测试检查流程控制；完整门禁中的五个场景执行真实 Docker 工作流。

| 检查 | 实际结果 | 退出码 | 证据 |
|---|---|---|---|
| 修改前完整服务测试 | 25 passed in 0.22s | 0 | `work/build-e7-zyl-before-20261108-025607/unit-tests/` |
| 修改后完整服务测试 | 26 passed in 0.19s | 0 | `work/build-e7-zyl-after-20261108-025607/unit-tests/` |
| 个人定向测试 | 一个通过标记 | 0 | `work/build-e7-zyl-after-20261108-025607/student-test.log`、`student-test-exit-code.txt` |

个人定向测试命令为：

```bash
docker run --rm --network none b08-e7-draft:241250011 \
  pytest tests/test_student_241250011_e7.py -q
```

## 3. 完整门禁结果

本次门禁命令为：

```bash
python3 scripts/lab_cloud.py gate \
  --image b08-e7-draft:241250011 \
  --candidate inputs/zyl-error-02/Dockerfile \
  --out work/e7-zyl-20261108-025607 \
  --build-timeout 7200
```

整体退出码为 `0`，`gate/gate-result.json` 的 `passed=true`、`intentional_failure=false`，六项检查全部通过。以下场景证据路径均相对于 `work/e7-zyl-20261108-025607/gate/`。

| 场景 | 输入或故障注入 | 预期与实际结果 | 工作流退出码 | 判定 | 证据 |
|---|---|---|---|---|---|
| unit-tests | 运行个人服务镜像内的测试 | 全部通过 | 0 | PASS | `unit-tests/stdout.log` |
| success | 本人 E5 的 error-02 候选 | 第一轮 MISSING_MAKE；第二轮成功；同一镜像输出 hello E3，SUCCEEDED | 0 | PASS | `success/evidence/result.json` |
| wrong-output | 将期望改为 intentionally wrong output | 检测输出不符，FAILED | 1 | PASS | `wrong-output/evidence/result.json` |
| invalid-candidate | 将候选 CMD 替换为 echo | 构建前拒绝，FAILED | 1 | PASS | `invalid-candidate/stdout.log` |
| build-failed | 插入 RUN exit 23 | 第二轮构建失败，停止运行验证，FAILED | 1 | PASS | `build-failed/evidence/result.json` |
| runtime-timeout | 初始与候选 CMD 同时增加 sleep 10，运行预算为 1 秒 | 第二轮成功后运行超时，TIMED_OUT，容器已移除 | 1 | PASS | `runtime-timeout/evidence/result.json`、`runtime-timeout/evidence/cleanup-check/stderr.log` |

故障场景的退出码为 1，门禁判定为 PASS，表示检测行为符合预期。invalid-candidate 在构建前被拒绝，没有 trace_id。

| 场景 | trace_id |
|---|---|
| success | `e6-b-09b3413507894491a3f7cffce1abeac3` |
| wrong-output | `e6-b-ae9ea8b987864025aa4910b3e496798c` |
| build-failed | `e6-b-da9e08c4b333488b9294ccdbc8164c39` |
| runtime-timeout | `e6-b-cf3a88c1bf4146c982b2c01158888983` |

## 4. 正常场景的同镜像验证

第一轮实际构建退出码为 `1`，分类为 `MISSING_MAKE`；第二轮退出码为 `0`，产生镜像：

```text
sha256:0363c3589ad85bdc2912a7f95e8ae13e6c4c1868bee3b978be9efc213e21c2bb
```

`verification.command` 的最后一个参数与该镜像 ID 相同。验证采用 `--network none`、1 CPU、128m 内存和 64 个进程上限，实际退出码为 `0`，标准输出为 `hello E3\n`，`output_matches=true`。

本场景 `elapsed_ms=1145`，表示核心工作流记录的耗时，不包含整个六项门禁的全部耗时。

## 5. 运行超时与容器清理

`fault-injection.json` 记录受控注入类型为 `DELAYED_CONTAINER_START`，延迟 10 秒，验证预算 1 秒。修改文件为场景副本中的 `fixture/Dockerfile.broken` 和 `candidate.Dockerfile`，项目源文件未修改。

超时场景第一轮仍为 `MISSING_MAKE`，第二轮构建退出码为 `0`，生成镜像：

```text
sha256:960c0c588f26ad0f2af7addd3fe969b1c0abd08a04fd7d6061241b072b4ce81d
```

随后工作流状态为 `TIMED_OUT`，错误为 `Docker client command exceeded 1s`。构建预算为 7200 秒，运行验证预算独立设置为 1 秒，本次验证的是运行超时。

受控 CMD 修改使候选哈希变为 `f5236f1da386bd59e9c3c054dc9c317816220f215a82659e2ed7c849e86f4e4c`。场景初始 Dockerfile 的哈希相应变化，`.dockerignore`、`Makefile`、`README.md` 和 `main.c` 与正常场景一致。

容器清理检查返回：

```text
Error response from daemon: No such container: ffc9076406d112c9fe93bd999157a40939ebc7d5f2e27632539e4d10509938aa
```

该结果与 runtime-timeout 的门禁通过记录共同确认运行容器已经移除。

## 6. CI 分工与证据索引

个人提交使用 `student/241250011/e7` 分支。仓库工作流 `.github/workflows/e7-quality-gate.yml` 的检查名称为 `e7-b-quality-gate`，CI 使用 `fixtures/ci-candidates/DeepSeek-E5.Dockerfile`，与本次云端显式传入的个人候选分别记录来源。

分支保护、故意失败 PR、普通合并被拒和修复后恢复合并由组长统一演示。本报告的个人实验结果为上述服务测试、扩展测试和云端六项门禁。

以下路径均相对于 `/root/241250011/B08-E7`。

| 文件或目录 | 内容 |
|---|---|
| `inputs/zyl-error-02/` | 个人候选、说明与 E5 来源记录 |
| `services/draft/tests/test_student_241250011_e7.py` | inspect 失败终止测试 |
| `work/build-e7-zyl-before-20261108-025607/unit-tests/` | 修改前完整测试及退出码 |
| `work/build-e7-zyl-after-20261108-025607/unit-tests/` | 修改后完整测试及退出码 |
| `work/build-e7-zyl-after-20261108-025607/student-test.log`、`student-test-exit-code.txt` | 个人定向测试及退出码 |
| `work/e7-zyl-20261108-025607/source-commit.txt`、`invocation.json` | 本次源码提交、入口时间、镜像和候选路线 |
| `work/e7-zyl-20261108-025607/input-candidate-sha256.txt`、`e5-provenance.json`、`candidate-origin.md` | 个人输入候选及来源 |
| `work/e7-zyl-20261108-025607/gate-exit-code.txt` | 门禁整体退出码 |
| `work/e7-zyl-20261108-025607/gate/gate-result.json`、`gate/results.csv` | 六项门禁汇总 |
| `work/e7-zyl-20261108-025607/gate/success/evidence/` | 两轮构建、镜像检查与运行验证 |
| `work/e7-zyl-20261108-025607/gate/wrong-output/`、`gate/invalid-candidate/`、`gate/build-failed/` | 故障场景输入、命令和结果 |
| `work/e7-zyl-20261108-025607/gate/runtime-timeout/` | 超时注入、构建、运行与清理检查 |
| `docs/zyl-E7验收记录.csv` | 个人验收表 |

原始 work 结果单独归档保存；个人候选、测试、报告和验收表通过 Git 提交。
