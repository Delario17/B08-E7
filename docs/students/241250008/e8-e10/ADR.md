# E8 决策记录

盛浩宇，241250008，2026-11-11。

使用同提交固定 MD 报告绑定受测项目 HEAD，旧报告以 STALE_REPORT 拒绝。对未知目标采用 UNSUPPORTED_TARGET 明确拒绝，并要求所有顶层源文件逐字节保持及 Git 状态干净。

E8 的直接声明风格补丁保留原 RD 和编译配方。受限显式规则便于建立独立预期，宏和混合声明风格在 E9 继续处理，候选质量在 E10 验证。

实际验证为 10 项测试通过，证据为 `work/student-tests.log` 和 `work/e8-B-manual.O54FTD/student-unknown-target-result.json`。

## E9 共享变量影响分析

盛浩宇，241250008，2026-11-11。选择手册中的共享变量影响分析自主任务，新增独立测试，将 main.o 和 helper.o 绑定同一 DEPS。通过精确声明集合和 RD 集合断言记录跨目标传播，同时保存原始输入和应用副本。

该选择展示参考 macro 策略的作用范围。验证为 11 项测试通过，独立证据为 `work/e9-B-manual.cj66BK/shared-variable-analysis/impact-summary.json`。后续目标局部修复可结合变量引用关系设计。
