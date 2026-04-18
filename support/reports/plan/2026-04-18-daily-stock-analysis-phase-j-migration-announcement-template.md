# Migration Announcement Template (`data_provider.*` -> canonical provider path)

## Subject
[Deprecation Notice] Legacy `data_provider.*` imports are entering migration window

## Message body

团队好，

`daily_stock_analysis` 已将运行时数据访问 canonical 路径迁移到：

- `src.stock_analysis_skill.providers.*`

旧路径：

- `data_provider.*`

目前仍可用，但仅作为兼容桥（compat-only），并进入退役治理窗口。

### 你需要做什么

请将所有新代码与现有自动化脚本导入改为 canonical 路径，例如：

```python
# before
from data_provider.base import normalize_stock_code

# after
from src.stock_analysis_skill.providers.base import normalize_stock_code
```

完整迁移说明：
- `references/provider-import-migration.md`

### 观测开关

如需排查遗留调用，请在非生产环境启用：

```bash
DSA_WARN_LEGACY_IMPORTS=1
```

### 计划窗口

- 当前：兼容桥保持可用
- 退役最早评估时间：不早于 `2026-07-31`（并需通过 Phase J 删除门禁）

如你负责的脚本无法及时迁移，请尽快回复：
- 调用仓库/脚本
- 预计迁移时间
- 是否存在阻塞
