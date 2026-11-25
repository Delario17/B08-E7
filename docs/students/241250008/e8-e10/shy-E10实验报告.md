# 盛浩宇 E10 B 轨道个人实验报告

姓名为盛浩宇，学号为 241250008，小组为 B08，轨道为 B，实验日期为 2026-11-25。

## 环境与代码版本

仓库为 [Delario17/B08-E7](https://github.com/Delario17/B08-E7)，个人分支为 `student/241250008/e8-e10`。开始时从 main 快进同步，基线 SHA 为 `1bb8e750d73a8e0952f1fadb1217d1e164fa1e42`。

服务器仓库为 `/root/241250008/E8/B08-E7`，个人镜像为 `course-e8e10:241250008`，镜像 ID 为 `sha256:17a965353ae4efcb22606950bd0b9c6cf9f8318ab838a568d60ae7a13ee07899`。系统为 Ubuntu 22.04 x86_64，实际可见内存约 1.7 GiB，低于手册建议的 4 GiB，实际实验和动态跟踪均通过。资源记录为 `work/e10-preparation/server-memory.txt`、`server-disk.txt`，工具链记录为 `work/toolchain.txt`。

学生测试源码 SHA 为 `fe6143e76714baa2e0d7d713ee310a07379c736b`，受测项目 C0 SHA 为 `7ae089b62065143594f4fc86dbdcf3a6faf78a9f`。实验源码版本与样例版本分别保存在 student-source-commit.txt 和 fixed-md-report.json。

## 实际执行与三项验证

在仓库根目录执行 `bash /root/241250008/E10/run_e10_manual.sh`，逐段执行 E10 B 手册第 1 至 10 步。基线实验目录为 `work/e10-B-manual.NNaYqG`，个人测试提交后的复检目录为 `work/e10-B-manual.DkVjCE`。各容器步骤退出码均为 0。

固定报告的 MD 为 main.o/config.h，候选在 main.o 依赖行中增加 config.h，保留 unused.h 和编译配方。报告、candidate.patch、patch-plan.json 和原输入均保存于本次 OUT。

| 场景 | 预期与实际 | 源文件判定 | 证据目录 |
|---|---|---|---|
| 故意错误测试 | 补丁应用和构建成功，预期 99 与实际 1 不符，checks.test=False，accepted=False | rollback=True，source_unchanged=True，cmp 退出 0 | reject-test/ |
| 正常候选 | patch_applies/build/test/header_change/no_missing 全部 True，accepted=True | 通过后写回 Makefile | accept/ |
| 无效补丁 | git apply --check 报错，accepted=False | rollback=True，source_unchanged=True，已接受的 Makefile 字节保持 | reject-patch/ |

表中证据路径均相对于 `work/e10-B-manual.DkVjCE/`。三份 validation.json、sandbox、可用构建/增量日志和重检报告均保存。results.csv 三行 passed=True，gate.json 为 passed=True、rows=3。

接受前后的独立字节副本为 source-before.Makefile 和 source-after-accept.Makefile。最终源项目仅有 Makefile 跟踪文件变化，源 config.h 的 VALUE 保持 1，accept/sandbox/config.h 中 VALUE 为 2。增量日志记录头文件变化后重新编译 main.o 与链接 app。

## 真实动态重检

调用真实 BuildChecker 完成最终项目重检，状态为 `SUCCEEDED`，trace_id 为 `e6-43c949818ac441488a171250bb569811`，findings 中没有 MISSING，保留 RD main.o/unused.h。原始证据在 `work/e10-B-manual.DkVjCE/recheck-buildchecker/`，包括 findings.json、trace、Make 数据库及构建日志。汇总核对为 `work/e10-B-manual.DkVjCE/verification-summary.json`。

## 自主任务与个人代码贡献

自主任务采用能够构建但仍存在 MD 的候选。在 `labs/e8e10/test_profile.py` 增加 `Student241250008E10Tests.test_buildable_candidate_with_missing_dependency_is_rejected`。

独立输入只将 CFLAGS 从 -O0 改为 -O1，保留缺少 config.h 的目标依赖。预期补丁可应用、构建成功、初始程序输出 1，但将 sandbox 中 VALUE 改为 2 后，Make 缺少触发关系，程序仍输出 1。动态头文件变化检查与 no_missing 均为 False，最终拒绝候选。

实际 checks 为 `{"patch_applies": true, "build": true, "test": true, "header_change": false, "no_missing": false}`，accepted=False、error=None、rollback=True。重检精确保留 MD main.o/config.h，原项目全部顶层文件 SHA-256 前后一致。独立输入、候选、validation.json、构建日志、incremental.log、recheck.json、sandbox 和字节保持核对位于 `work/e10-B-manual.DkVjCE/student-remaining-md/`。

基线为 16 项测试，新增后为 17 项，全部通过。命令为 `docker run --rm --network none --user 0:0 -e HOME=/tmp -v "$PWD:/course" -w /course course-e8e10:241250008 python3 -m unittest discover -s labs/e8e10 -p test_profile.py -v`。日志为 `work/e10-preparation/baseline-tests.log` 和 `student-tests.log`。

## 参考实现、机制与交接

fixture、scan、patch、validate 及 BuildChecker 对接来自小组参考实现。个人贡献为能够构建但保留 MD 的独立候选、回归测试、源文件保护证据和本报告。验证体现候选应用、构建、功能测试、头文件变化与依赖重检共同决定接受结果。

代码、测试与文档提交到 [本次 E10 PR](https://github.com/Delario17/B08-E7/pull/13)，供组长审阅合并。最新提交的 CI 元数据、PR 状态与已下载 artifact 保存于 `work/ci-e10/latest/`。最终 SHA、运行链接和备份信息见提交包中的 submission-index.json。

报告采用姓名缩写命名为 shy-E10实验报告.md，ADR 与 AI_USAGE 追加本次记录。服务器与电脑各保存一份完整代码和原始证据归档。
