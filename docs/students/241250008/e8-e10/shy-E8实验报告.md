# 盛浩宇 E8 B 轨道个人实验报告

姓名为盛浩宇，学号为 241250008，小组为 B08，轨道为 B，日期为 2026-11-11。

## 环境与版本

仓库为 [Delario17/B08-E7](https://github.com/Delario17/B08-E7)，个人分支为 `student/241250008/e8-e10`。开始时已同步 main，基线 SHA 为 `773772180425b10c7a0c6311612f0874bdca0846`。

服务器目录为 `/root/241250008/E8/B08-E7`。个人镜像为 `course-e8e10:241250008`，ID 为 `sha256:17a965353ae4efcb22606950bd0b9c6cf9f8318ab838a568d60ae7a13ee07899`。系统为 Ubuntu 22.04 x86_64，实际内存约 1.7 GiB。环境构建退出 0，日志为 `work/environment-build.log`。资源与工具链记录为 `work/server-memory.txt`、`work/server-disk.txt`、`work/toolchain.txt`。

学生测试源码 SHA 为 `8471e285622f6ab60bd54f27f0650e05a35ccb61`，受测样例 C0 SHA 为 `3108651de84e4128ab6302159e245a6eb661fdde`。报告 commit 与样例 HEAD 已核对一致。

## 实际命令与结果

在仓库根目录执行 `bash ../run_e8_manual.sh`，脚本逐段执行 E8 B 手册第 1 至 8 步，使用课堂辅助脚本进入个人容器。基线目录为 `work/e8-B-manual.iJxegm`，个人代码提交后的复检目录为 `work/e8-B-manual.O54FTD`。各步骤均退出 0。

| 检查项 | 独立预期与实际结果 | 证据文件 |
|---|---|---|
| 固定 MD | 精确 MISSING main.o/config.h、REDUNDANT main.o/unused.h，符合预期 | fixed-md-report.json |
| 报告身份 | commit 与样例 HEAD 一致 | fixed-md-report.json、步骤日志 |
| 目标定位 | main.o，config.h，style=direct | patch-plan.json |
| 候选补丁 | 增加 config.h，保留 unused.h 与编译配方 | candidate.patch |
| 应用检查 | git apply --check 成功，原项目干净 | steps/ |
| 旧报告 | STALE_REPORT，Makefile 原字节保持 | expected-failure.json、steps/ |
| 自主未知目标 | UNSUPPORTED_TARGET，全部源文件哈希保持 | student-unknown-target-result.json |

表中证据均位于 `work/e8-B-manual.O54FTD/`。原始输入、独立个人输入、结论和步骤日志保存在该目录，核对汇总为 `verification-summary.json`。

## 个人贡献与新增测试

在 `labs/e8e10/test_profile.py` 增加 `Student241250008E8Tests.test_unknown_target_is_rejected_without_source_changes`。测试创建独立样例，以同提交报告提供 MISSING unknown.o/config.h，断言精确错误 UNSUPPORTED_TARGET，比较所有顶层源文件的原始字节并检查 Git 工作区干净。

原小组基线为 9 项测试，个人新增后为 10 项，全部通过。测试命令为 `docker run --rm --network none --user 0:0 -e HOME=/tmp -v "$PWD:/course" -w /course course-e8e10:241250008 python3 -m unittest discover -s labs/e8e10 -p test_profile.py -v`。日志为 `work/baseline-tests.log` 和 `work/student-tests.log`。

fixture、scan、patch 和版本检查沿用最新小组参考代码。个人贡献为未知目标测试、独立拒绝证据、报告、ADR 和 AI 使用记录。

## 论文机制与覆盖范围

E8 对应 MDfixer 的缺失依赖定位、报告版本绑定和候选 Patch 生成。固定 MD 报告在本次运行中由 GCC 依赖采集生成，教学样例采用受限 C/Make 显式规则。E8 完成候选与应用检查，构建、测试和动态重检在 E10 阶段继续验证。

## GitHub 与交接

个人贡献提交到 [本次 E8 PR](https://github.com/Delario17/B08-E7/pull/10)。最终 CI 记录、head SHA、PR 快照和已下载 artifact 保存于 `work/ci-e8e10/latest/`，完整提交索引为提交包中的 `submission-index.json`。PR 的 Checks 页面提供对应运行链接。

公共 workflow 自动回归两个轨道的 E8—E10 演示。本次个人手工实验范围为 E8 B。个人 PR 交给组长审阅和合并。

报告采用姓名缩写命名为 `shy-E8实验报告.md`，个人文档位于 `docs/students/241250008/e8-e10/`。服务器保留完整原始证据，提交包另行备份至电脑。
