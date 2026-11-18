# 决策记录

## 背景与约束

MDfixer 接收与某个受测提交绑定的 MD 报告，为显式 Make 依赖生成候选补丁。课程 profile 只支持 `main.o`、`helper.o`、有限的 CFLAGS 和 direct/macro/mixed 三种声明形式；REDUNDANT 发现必须保留。任何失败都不能破坏原项目。

## 选择与替代方案

### 报告身份

选择：生成 patch 前强制比较报告 commit 与项目 HEAD，不一致立即返回 `STALE_REPORT`。

替代方案：尝试把旧报告重新解释到新源码。拒绝该方案，因为报告中的目标和依赖边可能已失效，自动迁移会掩盖输入身份错误。

### 声明风格与共享变量

选择：direct 修改目标依赖行；只有目标依赖完整等于单一宏引用时，macro 修改宏定义；mixed 保留宏引用并在目标行增加依赖。课程实现允许 macro 修改共享变量，但报告必须说明它可能影响其他引用目标。

替代方案：所有风格统一修改目标行。该方案局部性更强，但会破坏 macro 风格的表达意图，因此未采用。后续扩展应在修改宏前分析全部引用点，发现跨目标影响时要求人工确认或回退到局部修改。

### 失败保护

选择：把项目复制到独立 sandbox，依次执行 `git apply --check`、应用 patch、全量构建、功能测试、头文件变化后的增量构建和 MD 重检；只有全部成功才将 sandbox 的 Makefile 写回原目录。

替代方案：在原目录应用后失败时反向 patch。拒绝该方案，因为构建过程还可能生成或改变其他文件，反向 patch 不能证明目录完全恢复。

## 代价与覆盖范围

复制项目和重复构建增加时间与磁盘开销，但换来明确的 `source_unchanged` 和 rollback 证据。当前实现不解析复杂 Make 语法，也不会删除 RD；这些限制在错误拒绝优先的教学场景中是可接受的。

## 验证命令与实际证据

- 单元测试：`python3 -m unittest discover -s labs/e8e10 -p test_profile.py -v`，16 项全部通过。
- E8：`work/e8-B-manual.5qP4f4/expected-failure.json` 记录 `STALE_REPORT`。
- E9：`work/e9-B-manual.NEGO6y/` 保存三种输入、patch、plan 和 apply-demo。
- E10：`work/e10-B-manual.2JjL0z/gate.json` 为 `passed=true`、`rows=3`；最终 BuildChecker 无 MISSING。
