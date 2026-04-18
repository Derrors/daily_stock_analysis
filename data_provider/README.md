# data_provider (compat-only)

这个目录已退役为 **legacy import compatibility bridge**。

## Canonical path
运行时数据访问实现已迁移到：

- `src.stock_analysis_skill.providers`

新代码禁止再从 `data_provider.*` 导入。

## 兼容行为
- `data_provider/*` 模块只做 alias/转发，不承载业务实现。
- 默认不打印 deprecation warning。
- 如需排查历史调用，可设置环境变量：
  - `DSA_WARN_LEGACY_IMPORTS=1`

## 退役窗口
- 当前阶段：保持兼容桥可用。
- 计划：最早在 **Phase J** 开始评估移除（且不早于 `2026-07-31`），移除前会先完成全仓与外部调用方审计。
