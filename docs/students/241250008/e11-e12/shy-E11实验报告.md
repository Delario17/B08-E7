# 盛浩宇 E11 B 轨道个人报告

姓名为盛浩宇，学号为 241250008，小组为 B08，轨道为 B，日期为 2026-11-27。

## 代码与环境

仓库为 [Delario17/B08-E7](https://github.com/Delario17/B08-E7)，个人分支为 `student/241250008/e11-e12-integration`。最新 main 基线为 `09654d0cf29bb206ebb33abf44fa4a3d0df0b1ba`。公共集成代码从组内准备分支提交 `e1acb00349a5c3281bf77ff5d61da0ec75ee5f8f` 增量导入，包含运行入口、E11/E12 模块、工作流及其依赖的 MakeProfile 兼容接口。

学生测试源码 SHA 为 `9d07d70e54e2ded03f73544d5ae13e9335307ea3`，运行记录保存在 `/root/241250008/E8/B08-E7/work/`。专属镜像为 `course-e11e12:241250008`，镜像 ID 为 `sha256:4b8ea48c5ca9d0e80aab2962aa606b32f0a46b3d39638e7af5cfd639831326bf`。服务器为 Ubuntu 22.04 x86_64，实际内存约 1.7 GiB。

初次 Docker Hub 下载超时后，使用 DOCKER_CLI_IMAGE 构建参数切换到相同 digest 的镜像地址，日志为 `work/e11-preparation/build-mirror.log`。个人样例候选使用 DaoCloud 和清华 APT 源，固定基础镜像 digest，dataset.json 保存调整说明和候选 SHA-256。

## 输入与实际运行

先完成 build、test、prepare。随后从课程 fixture 创建两组个人控制样例，分别使用 direct 与 macro 声明。每组拥有真实内部 Git C0/C1，C1 新增 extra.h 包含，固定 MD 输入由该提交上的 scan 生成，并将外层与内层 commit 都绑定到目标提交。样例来源标记为 course-generated controlled C/Make fixture。

实际入口为 `python3 run_e11e12.py run --request data/241250008-e11-风格/request.json --out work/e11-风格-241250008-01`，实际命令及退出码见 `work/e11-preparation/`。

| 场景 | 实际结果 | job_id | trace_id |
|---|---|---|---|
| direct 基线 | SUCCEEDED，退出 0 | job-c9dcbb3133224a0b9db41d2fef5e5984 | trace-0980b1a8ee7d4e1e9e03be2eb79817bc |
| macro 自主扩展 | SUCCEEDED，退出 0 | job-251ffe666cf94bf1b3861a53f8af3b02 | trace-07d65099288e4135a2616fb5624ad443 |
| 过期固定报告 | FAILED / STALE_REPORT，符合预期拒绝 | job-b64f2260bb02438cb7aaf8cb9c3e2f23 | trace-1538ecd06d6a440496e902806f42afc8 |

每个场景的完整输出目录为 `work/e11-direct-241250008-01`、`work/e11-macro-241250008-01`、`work/e11-stale-241250008-01`。目标提交和候选来源见各 data 目录的 dataset.json，输入请求随结果保存为 request.json。

## DRAFT 与 MDFixer 核对

direct 与 macro 的第一轮真实构建均分类为 MISSING_MAKE，第二轮实际构建退出 0。最终镜像运行退出 0，输出为 1，运行命令中的镜像 ID 与第二轮构建结果一致。完整 Docker 日志为各输出下的 draft-build/iter-01 与 iter-02。

固定报告包含 MD main.o/config.h、MD main.o/extra.h 和 RD main.o/unused.h。两条 MD 均生成补丁，direct 修改目标行，macro 修改 DEPS 定义为 `main.c unused.h config.h extra.h`，目标仍引用 `$(DEPS)`。两种候选的五项 validation checks 全部为 True，accepted=True。最终真实 BuildChecker 重检只保留 RD main.o/unused.h。

封装报告为 draft.json、fixed-md.json、repair.json、recheck.json，各报告使用同一 job_id/trace_id，并绑定目标 commit。result.json、封装报告、原始日志、candidate.patch、repair-plan.json、validation/ 和 final-full/ 全部保留。所有产物 URI、SHA-256 和字节长度已逐项核对，结果保存为各目录下的 verification.json。

过期场景只修改报告外层 commit 为全 0，真实 DRAFT 构建通过后报 STALE_REPORT。流程停在修复前，阶段列表仅含 draft，目标 Makefile 工作副本保持原字节。错误原文保存在 result.json。E11 使用固定 MD 输入，后续 E12 才接入增量检测实际报告与跨组 API 联调。

## 个人测试与贡献

新增 `labs/e11e12/test_student_241250008.py`，包含 macro 双 MD 修复和内层过期 commit 拒绝两项测试。macro 测试独立断言两项编辑、变量引用、编译配方字节保持及重检精确 RD 集合。过期测试保持报告外层 commit 正确、只破坏 data.commit，用受控 DRAFT 响应隔离版本检查，要求 STALE_REPORT，确认 patch 和项目验证调用均未发生。

契约测试由 12 项增加到 14 项，全部通过，日志为 `work/e11-preparation/baseline-tests.log` 和 student-tests.log。E8—E10 兼容回归和集成工作流随最终提交在 CI 执行，运行信息及下载 artifact 见 `work/ci-e11/latest/`。

公共 pipeline、版本化封装和 MakeProfile 接口来自组内准备分支。个人贡献为两项独立测试、direct/macro 实际运行、过期报告场景、产物核对和个人报告。候选采用已保存课程模式进行下载源适配，未调用模型 API 重新生成。

## GitHub 与提交

个人贡献提交到 [本次 E11 PR](https://github.com/Delario17/B08-E7/pull/15)，供组长审阅合并。最终提交 SHA、真实运行链接、CI 下载记录和服务器位置由提交包中的 submission-index.json 索引。个人报告采用姓名缩写命名为 shy-E11实验报告.md。
