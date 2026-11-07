# E7-B 完整验证与个人边界测试报告（241250078 孙博一）

## 1. 基本信息

- 小组/轨道：B08 / B（DRAFT）
- 姓名/学号：孙博一 / 241250078
- 实验日期：2026-11-07（Asia/Shanghai）
- 仓库：`https://github.com/Delario17/B08-E7`
- 服务器目录：`/root/241250078/B08-E7`
- 基线 main：`e6b0a4aa9734f35ec98edc9c5e33ddad801b9891`
- 本人测试提交：`289fd3aca4b21cf16ae021a2b0013ea7567f1044`
- 分支：`student/241250078/e7`

## 2. 本人新增边界测试

新增 `services/draft/tests/test_student_241250078_e7.py`。已有测试覆盖 `/bin/sh: 1: make: not found`，本测试增加另一种常见 shell 文本：

```text
/bin/sh: 1: make: command not found
```

预期 `classify_failure` 同样返回 `MISSING_MAKE`。它与仓库已有的多阶段候选测试不重复。

定向运行结果为 `1 passed`、退出码 0，证据位于 `work/e7-241250078-targeted/`。

## 3. 服务构建与完整测试

```bash
python3 scripts/lab_cloud.py build \
  --image course1027-draft:241250078 \
  --out work/e7-241250078-build --build-timeout 1200
```

- 构建入口退出码：0
- 完整单元测试：`26 passed in 0.20s`
- 服务镜像：`course1027-draft:241250078`
- 服务镜像 ID：`sha256:281252949e052cee2daa30979b85c92f6d9f7658e1f525da1ed8bd6d7d4d3045`

## 4. 完整 Gate

```bash
python3 scripts/lab_cloud.py gate \
  --image course1027-draft:241250078 --replay \
  --out work/e7-241250078-gate --build-timeout 1200
```

Gate 整体退出码为 0，`gate-result.json` 的 `passed=true`。六项检查如下：

| 场景 | passed | 工作流状态/退出码 | 结果 |
|---|---:|---|---|
| unit-tests | true | 退出 0 | 镜像内 26 项测试通过 |
| success | true | SUCCEEDED / 0 | 两轮构建成功，同一镜像 ID 禁网运行并输出 `hello E3` |
| wrong-output | true | FAILED / 1 | 故意错误的期望输出被正确拒绝 |
| invalid-candidate | true | FAILED / 1 | 修改 CMD 的非法候选在构建前拒绝 |
| build-failed | true | FAILED / 1 | 注入 `RUN exit 23`，第二轮构建失败且停止验证 |
| runtime-timeout | true | TIMED_OUT / 1 | 延迟 10 秒、预算 1 秒，正确超时并清理容器 |

超时清理检查对保存的容器 ID 执行 inspect，Docker 返回 `No such container`，证明超时容器已经删除。

证据哈希：

- `gate-result.json`：`d486ed244a8e0939a2cb07bfcb3376fd7377f75f04c94f0590ba1a82a7e12a95`
- `results.csv`：`2487fb4f3d741419a09dc9e810e1019a79052d5259279540464e0e50d9cd4391`

## 5. 三类返回值

工作流 `status` 描述工具实际终态；CLI 退出码供调用者判断本次运行；`case.passed` 表示结果是否符合故障场景的预期。因此故意注入错误的场景可以是状态 `FAILED`、退出码 1，但场景本身 `passed=true`。

## 6. GitHub CI

本仓库已包含 `.github/workflows/e7-quality-gate.yml`，分支 push 和 PR 会触发 `e7-b-quality-gate`。个人分支推送后应保存对应 Actions 运行和 PR 检查链接。

main 分支保护、故意失败 PR 的合并拦截以及同一 PR 修复恢复属于组长使用管理员权限执行一次的共同任务；个人报告不将尚未取得的组级证据标为完成。

## 7. 证据索引

| 内容 | 服务器相对路径 |
|---|---|
| 服务构建、镜像检查和 26 项测试 | `work/e7-241250078-build/` |
| 个人边界测试定向结果 | `work/e7-241250078-targeted/` |
| Gate 包装命令与退出码 | `work/e7-241250078-gate/driver/` |
| Gate 汇总 | `work/e7-241250078-gate/gate/gate-result.json` |
| 六项结果表 | `work/e7-241250078-gate/gate/results.csv` |
| 各场景原始输入、日志和报告 | `work/e7-241250078-gate/gate/<case>/` |
| 超时故障说明 | `work/e7-241250078-gate/gate/runtime-timeout/fault-injection.json` |
| 超时容器清理核验 | `work/e7-241250078-gate/gate/runtime-timeout/evidence/cleanup-check/` |

`work/` 不进入 Git，将在服务器个人提交目录中单独归档。
