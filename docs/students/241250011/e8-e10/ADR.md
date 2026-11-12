# ADR：按 Makefile 声明风格生成缺失依赖补丁

| 项目 | 记录 |
|---|---|
| 作者 | 朱雨乐，241250011，B08，B 轨道 |
| 实验范围 | E8、E9 |
| 关联实现 | `labs/e8e10/lab.py` 中的 `patch()` |
| 个人验证代码 | `d9ae358ba6a47cbd4e14e31436faabfc4d42b613` |

## 背景

样例的 `main.o` 缺少 `config.h` 的声明，同时声明了源码未使用的 `unused.h`。修复任务要根据同一版本的依赖报告定位声明，生成可以审阅和检查的补丁，并保留原始样例用于对照。

## 采用的方案

1. 以样例 Git HEAD 校验报告的 `commit` 字段。提交不一致时返回 `STALE_REPORT`。目标无法定位时返回 `UNSUPPORTED_TARGET`。
2. 候选补丁处理 MISSING 条目。保留已有的 RD 声明和编译配方，将补丁范围限定为本次缺失依赖。
3. direct 在目标依赖行补齐 `config.h`。纯 macro 修改 `DEPS` 定义，保持 `main.o: $(DEPS)`。mixed 保留 `$(HEADERS)` 引用，在目标行补齐 `config.h`。
4. 生成统一 diff 与结构化 plan，以 `git apply --check` 检查补丁。E9 的实际应用放在独立的 `apply-demo/` 副本，使补丁后的 Makefile 可以与原始 macro 样例逐项对照。
5. 沿用教学实现，在个人测试中增加未知目标拒绝和 macro 应用后重检两个断言场景。

## 方案取舍

| 方案 | 影响 |
|---|---|
| 按原声明风格定位修改 | 改动集中在原有声明位置，便于审阅。需要分别识别目标行、纯变量引用和混合引用。 |
| 展开变量后统一改写目标行 | 补丁生成规则更统一，但变量定义与目标之间的组织关系会被消除。 |
| 生成候选后直接应用到源目录 | 应用结果可以立即查看，原输入需要借助版本历史恢复才能进行对照。独立副本能同时保留输入和应用结果。 |

变量定义可能被多个目标引用。本次 macro 样例中的 `DEPS` 由 `main.o` 使用。处理共享变量时，应先核对引用位置，再决定在目标行局部增加依赖、拆分变量或拒绝无法确定影响范围的候选。

## 验证证据

- E8 的 `work/e8-B-manual.Bjk6s8/patch-plan.json` 记录唯一操作 `main.o/config.h/direct`，`expected-failure.json` 记录 `STALE_REPORT`。
- E9 的 `work/e9-B-manual.ADoOSF/` 保存三份补丁和 plan。副本中的 `DEPS = main.c unused.h config.h` 与 `main.o: $(DEPS)` 同时保留。
- 个人测试断言未知目标返回 `UNSUPPORTED_TARGET` 并保持源文件。macro 用例断言应用后保留变量引用，重检仅剩原有的冗余依赖。两项个人测试均通过，完整测试为 11 项通过，耗时 0.351 秒，退出码为 0。测试记录见 `work/unit-tests-20261112-175023.log` 及同名 `.exit-code.txt`。
- 首次 E8/E9 运行对应源码提交 `7737721`，重跑对应个人测试提交 `d9ae358`。四次步骤退出码均为 0，环境镜像 ID 一致。
