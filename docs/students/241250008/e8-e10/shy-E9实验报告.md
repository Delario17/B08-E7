# 盛浩宇 E9 B 轨道个人实验报告

姓名为盛浩宇，学号为 241250008，小组为 B08，轨道为 B，日期为 2026-11-11。

## 仓库、环境与版本

仓库为 [Delario17/B08-E7](https://github.com/Delario17/B08-E7)，个人分支为 `student/241250008/e8-e10`，继续更新 [个人 PR #10](https://github.com/Delario17/B08-E7/pull/10)。

服务器仓库为 `/root/241250008/E8/B08-E7`，本次 E9 证据目录为 `work/e9-B-manual.cj66BK`。沿用个人镜像 `course-e8e10:241250008`，镜像 ID 为 `sha256:17a965353ae4efcb22606950bd0b9c6cf9f8318ab838a568d60ae7a13ee07899`。系统为 Ubuntu 22.04 x86_64，实际内存约 1.7 GiB。工具链见 `work/toolchain.txt`，本次资源信息见 `work/e9-preparation/`。

E9 学生测试源码 SHA 为 `b474bf232ee4d2c3a27de2cae6987b0588efc29a`。开始状态与同步记录见 `work/e9-preparation/base-source-sha.txt`。受测样例内部提交分别为下表中的 SHA。

| 风格 | 样例内部提交 SHA | 预期与实际修改位置 | 结论 |
|---|---|---|---|
| direct | d28b16cdd26a39b7c29e325252176e7cfd5a50af | main.o 目标依赖行增加 config.h | PASS |
| macro | 3a644ab1ee1a6e3762072ffeb3eec00301669218 | DEPS 定义增加 config.h，main.o 保持变量引用 | PASS |
| mixed | 66acd0ef394152a482cf6dc42cef1857b7b30704 | main.o 目标行增加 config.h，保留 HEADERS 引用 | PASS |

## 实际执行与证据

在仓库根目录执行 `bash /root/241250008/E9/run_e9_manual.sh`，逐段执行 E9 B 手册第 1 至 6 步。脚本调用课堂辅助命令创建新 OUT，并保存容器步骤日志。基线目录为 `work/e9-B-manual.LgRuwe`，新增个人代码后的复检目录为 `work/e9-B-manual.cj66BK`。

三种风格均保存 `<style>-input.json`、`<style>.patch`、`<style>-plan.json` 及原始项目。报告中的精确发现均为 MD main.o/config.h 与 RD main.o/unused.h，计划的 style 分别为 direct、macro、mixed。各补丁通过 git apply --check，三份原始项目 Git 工作区均干净。

macro 候选另行应用到 `apply-demo/`，实际 DEPS 为 `main.c unused.h config.h`，main.o 仍使用 DEPS。原 macro 输入保留原字节。编译配方和 unused.h 保留。结论、步骤日志和程序化核对汇总分别位于 `结论.txt`、`steps/`、`verification-summary.json`。

## 自主任务与个人代码贡献

自主任务选用共享变量影响分析。在 `labs/e8e10/test_profile.py` 新增 `Student241250008E9Tests.test_shared_macro_adds_dependency_to_both_targets`。

独立输入使 main.o 与 helper.o 同时引用 DEPS，helper.o 的直接依赖行写为 `helper.c $(DEPS)`。候选为 main.o 补充 config.h 时，修改共享 DEPS 定义，因此 helper.o 的声明依赖也增加 config.h。

独立预期为 helper.o 的声明依赖由 helper.c/main.c/unused.h 增加到 config.h/helper.c/main.c/unused.h。应用后精确发现集合为 RD main.o/unused.h、RD helper.o/config.h、RD helper.o/main.c、RD helper.o/unused.h。测试同时检查宏引用、候选生成阶段原字节保持、编译配方字节一致及精确计划。

测试总数由 10 项增加至 11 项，全部通过。命令为 `docker run --rm --network none --user 0:0 -e HOME=/tmp -v "$PWD:/course" -w /course course-e8e10:241250008 python3 -m unittest discover -s labs/e8e10 -p test_profile.py -v`。基线与个人测试日志分别为 `work/e9-preparation/baseline-tests.log`、`student-tests.log`。

额外独立证据保存于 `work/e9-B-manual.cj66BK/shared-variable-analysis/`，包括原始项目、应用副本、前后报告、shared.patch、计划及 impact-summary.json。原始项目全部顶层文件 SHA-256 前后一致，应用副本出现预期跨目标影响。

## 机制、限制与贡献范围

本次对应 MDfixer 对 direct/macro/mixed 声明风格的增补位置选择。共享变量使一个目标的修复传播到其他引用目标，个人测试和证据明确记录这一影响。后续可基于变量引用关系选择目标局部修复，并补充相关验证。

fixture、scan、patch 及三种风格策略来自小组参考实现。个人新增内容为共享变量影响测试、独立对照输入和报告。E9 完成候选生成及应用检查，候选构建、测试和动态质量验证由 E10 继续处理。

## CI、提交与交接

本次更新个人 PR #10，交给组长审阅合并。最终提交的 CI 元数据、PR 快照和已下载 artifact 位于 `work/ci-e9/latest/`，提交包中的 `submission-index.json` 保存最终 SHA 和实际运行链接。E9 报告采用姓名缩写命名为 `shy-E9实验报告.md`。

公共 workflow 自动执行两个轨道 E8—E10 的回归演示。本报告的个人分步实验范围为 E9 B。
